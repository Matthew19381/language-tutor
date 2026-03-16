import json
import logging
import os
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.models.lesson import Lesson
from backend.models.study_plan import StudyPlan
from backend.models.test_result import TestResult
from backend.models.flashcard import Flashcard
from backend.services.lesson_generator import generate_daily_lesson
from backend.services.audio_service import generate_vocabulary_audio, AUDIO_DIR
from backend.services.pdf_service import generate_lesson_pdf, EXPORTS_DIR
from backend.services.obsidian_service import save_obsidian_md

logger = logging.getLogger(__name__)
router = APIRouter()


def get_day_number(user: User) -> int:
    """Calculate which day number the user is on."""
    if not user.created_at:
        return 1
    delta = date.today() - user.created_at.date()
    return max(1, delta.days + 1)


def get_recent_errors(user_id: int, db: Session, limit: int = 10) -> list:
    """Get recent test errors for the user."""
    recent_tests = db.query(TestResult).filter(
        TestResult.user_id == user_id
    ).order_by(TestResult.created_at.desc()).limit(5).all()

    errors = []
    for test in recent_tests:
        if test.errors:
            try:
                test_errors = json.loads(test.errors)
                errors.extend(test_errors[:3])
            except Exception:
                pass

    return errors[:limit]


@router.get("/api/lessons/today/{user_id}")
async def get_today_lesson(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    day_number = get_day_number(user)

    # Check if lesson for today already exists
    today_start = datetime.combine(date.today(), datetime.min.time())
    existing_lesson = db.query(Lesson).filter(
        Lesson.user_id == user_id,
        Lesson.day_number == day_number,
        Lesson.created_at >= today_start
    ).first()

    if existing_lesson:
        content = json.loads(existing_lesson.content)
        return {
            "lesson_id": existing_lesson.id,
            "day_number": existing_lesson.day_number,
            "title": existing_lesson.title,
            "topic": existing_lesson.topic,
            "content": content,
            "is_completed": existing_lesson.is_completed,
            "created_at": existing_lesson.created_at.isoformat()
        }

    # Get active study plan
    study_plan = db.query(StudyPlan).filter(
        StudyPlan.user_id == user_id,
        StudyPlan.is_active == True
    ).first()

    if not study_plan:
        raise HTTPException(status_code=404, detail="No active study plan. Please complete placement test first.")

    study_plan_data = json.loads(study_plan.plan_data)

    # Get recent errors to incorporate in lesson
    user_errors = get_recent_errors(user_id, db)

    # Get recent topics for interleaving (last 7 days)
    week_ago = datetime.combine(date.today() - timedelta(days=7), datetime.min.time())
    recent_lessons = db.query(Lesson).filter(
        Lesson.user_id == user_id,
        Lesson.created_at >= week_ago
    ).order_by(Lesson.created_at.desc()).limit(7).all()
    recent_topics = [l.topic for l in recent_lessons if l.topic] if recent_lessons else None

    # Generate new lesson
    lesson_content = await generate_daily_lesson(
        day_number=day_number,
        study_plan_data=study_plan_data,
        user_errors=user_errors,
        cefr_level=user.cefr_level,
        language=user.target_language,
        native_language=user.native_language,
        recent_topics=recent_topics
    )

    # Save lesson to DB
    lesson = Lesson(
        user_id=user_id,
        day_number=day_number,
        title=lesson_content.get("title", f"Day {day_number} Lesson"),
        topic=lesson_content.get("topic", "General"),
        content=json.dumps(lesson_content),
        cefr_level=user.cefr_level,
        language=user.target_language,
        is_completed=False
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)

    # Extract vocabulary and create flashcards
    vocabulary = lesson_content.get("vocabulary", [])
    for vocab_item in vocabulary:
        word = vocab_item.get("word", "")
        translation = vocab_item.get("translation", "")
        if word and translation:
            # Check if flashcard already exists
            existing = db.query(Flashcard).filter(
                Flashcard.user_id == user_id,
                Flashcard.word == word
            ).first()
            if not existing:
                flashcard = Flashcard(
                    user_id=user_id,
                    word=word,
                    translation=translation,
                    example_sentence=vocab_item.get("example", ""),
                    language=user.target_language,
                    cefr_level=user.cefr_level
                )
                db.add(flashcard)

    db.commit()

    return {
        "lesson_id": lesson.id,
        "day_number": lesson.day_number,
        "title": lesson.title,
        "topic": lesson.topic,
        "content": lesson_content,
        "is_completed": lesson.is_completed,
        "created_at": lesson.created_at.isoformat()
    }


@router.get("/api/lessons/{lesson_id}")
async def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    content = json.loads(lesson.content)
    return {
        "lesson_id": lesson.id,
        "day_number": lesson.day_number,
        "title": lesson.title,
        "topic": lesson.topic,
        "content": content,
        "is_completed": lesson.is_completed,
        "created_at": lesson.created_at.isoformat()
    }


class CompleteLessonRequest(BaseModel):
    user_id: Optional[int] = None


@router.post("/api/lessons/{lesson_id}/complete")
async def complete_lesson(
    lesson_id: int,
    request: CompleteLessonRequest,
    db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    newly_awarded = []
    if not lesson.is_completed:
        lesson.is_completed = True
        lesson.completed_at = datetime.utcnow()

        # Award XP for completing lesson
        if request.user_id:
            user = db.query(User).filter(User.id == request.user_id).first()
            if user:
                user.total_xp += 25  # 25 XP for completing a lesson
                # Update streak
                if user.created_at:
                    days_since_start = (date.today() - user.created_at.date()).days
                    user.streak_days = days_since_start + 1

        db.commit()

        # Check achievements after commit
        if request.user_id:
            from backend.services.achievement_service import check_and_award_achievements
            user = db.query(User).filter(User.id == request.user_id).first()
            if user:
                newly_awarded = check_and_award_achievements(user, db)

    return {
        "success": True,
        "lesson_id": lesson.id,
        "is_completed": lesson.is_completed,
        "completed_at": lesson.completed_at.isoformat() if lesson.completed_at else None,
        "xp_awarded": 25,
        "new_achievements": newly_awarded,
    }


@router.get("/api/lessons/audio/{lesson_id}")
async def get_lesson_audio(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    content = json.loads(lesson.content)
    vocabulary = content.get("vocabulary", [])

    try:
        audio_files = await generate_vocabulary_audio(
            vocabulary=vocabulary,
            language=lesson.language,
            lesson_id=lesson_id
        )
        return {
            "lesson_id": lesson_id,
            "audio_files": audio_files
        }
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")


@router.get("/api/lessons/{lesson_id}/export-pdf")
async def export_lesson_pdf(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    content = json.loads(lesson.content)
    lesson_data = {
        "title": lesson.title,
        "topic": lesson.topic,
        "content": content,
    }

    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in lesson.title)[:50]
    filename = f"lesson_{lesson_id}_{safe_title}.pdf"
    output_path = os.path.join(EXPORTS_DIR, filename)

    try:
        generate_lesson_pdf(lesson_data, output_path)
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=filename,
        )
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.get("/api/lessons/{lesson_id}/export-obsidian")
async def export_lesson_obsidian(
    lesson_id: int,
    day_offset: int = Query(0, description="-1=yesterday, 0=today, 1=tomorrow, 2=day after"),
    upload: bool = Query(False, description="Upload to Google Drive instead of downloading"),
    db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    content = json.loads(lesson.content)
    lesson_data = {
        "title": lesson.title,
        "topic": lesson.topic,
        "content": content,
        "cefr_level": lesson.cefr_level,
        "language": lesson.language,
        "day_number": lesson.day_number,
    }

    # If day_offset > 0, pre-generate a future lesson
    if day_offset > 0:
        user = db.query(User).filter(User.id == lesson.user_id).first()
        if user:
            study_plan = db.query(StudyPlan).filter(
                StudyPlan.user_id == user.id,
                StudyPlan.is_active == True
            ).first()
            if study_plan:
                future_day = lesson.day_number + day_offset
                plan_data = json.loads(study_plan.plan_data)
                try:
                    future_content = await generate_daily_lesson(
                        day_number=future_day,
                        study_plan_data=plan_data,
                        user_errors=[],
                        cefr_level=user.cefr_level,
                        language=user.target_language,
                        native_language=user.native_language,
                        recent_topics=[lesson.topic]
                    )
                    lesson_data = {
                        "title": future_content.get("title", f"Day {future_day}"),
                        "topic": future_content.get("topic", ""),
                        "content": future_content,
                        "cefr_level": user.cefr_level,
                        "language": user.target_language,
                        "day_number": future_day,
                    }
                except Exception as e:
                    logger.error(f"Could not pre-generate future lesson: {e}")

    filepath = save_obsidian_md(lesson_data, lesson_id)

    if upload:
        try:
            from backend.services.google_drive_service import upload_to_google_drive
            folder_id = os.environ.get("GDRIVE_FOLDER_ID")
            url = upload_to_google_drive(filepath, folder_id)
            return {"success": True, "url": url, "filename": os.path.basename(filepath)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Google Drive upload failed: {e}")

    return FileResponse(
        filepath,
        media_type="text/markdown",
        filename=os.path.basename(filepath),
    )


@router.get("/api/lessons/list/{user_id}")
async def list_lessons(user_id: int, db: Session = Depends(get_db)):
    lessons = db.query(Lesson).filter(
        Lesson.user_id == user_id
    ).order_by(Lesson.day_number.asc()).all()

    return {
        "lessons": [
            {
                "lesson_id": l.id,
                "day_number": l.day_number,
                "title": l.title,
                "topic": l.topic,
                "is_completed": l.is_completed,
                "cefr_level": l.cefr_level,
                "created_at": l.created_at.isoformat()
            }
            for l in lessons
        ],
        "total": len(lessons),
        "completed": sum(1 for l in lessons if l.is_completed)
    }

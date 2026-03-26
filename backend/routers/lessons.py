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
from backend.services.audio_service import generate_vocabulary_audio, generate_full_lesson_audio, AUDIO_DIR
from backend.services.pdf_service import generate_lesson_pdf, EXPORTS_DIR
from backend.services.obsidian_service import save_obsidian_md
from backend.services.gemini_service import generate_json as ai_generate_json

logger = logging.getLogger(__name__)
router = APIRouter()


def get_day_number(user: User, db: Session = None, language: str = None) -> int:
    """Calculate which day number the user is on for a specific language.
    Uses per-language lesson count so each language starts at day 1."""
    if db is not None and language is not None:
        count = db.query(Lesson).filter(
            Lesson.user_id == user.id,
            Lesson.language == language,
            Lesson.is_completed == True
        ).count()
        return count + 1
    # Fallback: global calendar-based calculation
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

    # Check if today's lesson already exists for this language
    today_start = datetime.combine(date.today(), datetime.min.time())
    existing_lesson = db.query(Lesson).filter(
        Lesson.user_id == user_id,
        Lesson.language == user.target_language,
        Lesson.created_at >= today_start
    ).first()

    # If no lesson today, check for uncompleted lesson from previous days
    if not existing_lesson:
        existing_lesson = db.query(Lesson).filter(
            Lesson.user_id == user_id,
            Lesson.language == user.target_language,
            Lesson.is_completed == False
        ).order_by(Lesson.created_at.desc()).first()

    day_number = get_day_number(user, db, user.target_language)

    if existing_lesson:
        content = json.loads(existing_lesson.content)
        return {
            "lesson_id": existing_lesson.id,
            "day_number": existing_lesson.day_number,
            "title": existing_lesson.title,
            "topic": existing_lesson.topic,
            "content": content,
            "is_completed": existing_lesson.is_completed,
            "language": existing_lesson.language,
            "cefr_level": existing_lesson.cefr_level,
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
        title=lesson_content.get("title", f"Dzień {day_number}"),
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
                    cefr_level=user.cefr_level,
                    lesson_id=lesson.id,
                    lesson_day=lesson.day_number,
                    lesson_topic=lesson.topic
                )
                db.add(flashcard)

    db.commit()

    # Generate audio for lesson sections (background, non-blocking)
    import asyncio
    asyncio.create_task(
        generate_full_lesson_audio(lesson_content, user.target_language, lesson.id)
    )

    return {
        "lesson_id": lesson.id,
        "day_number": lesson.day_number,
        "title": lesson.title,
        "topic": lesson.topic,
        "content": lesson_content,
        "is_completed": lesson.is_completed,
        "language": lesson.language,
        "cefr_level": lesson.cefr_level,
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
        "language": lesson.language,
        "cefr_level": lesson.cefr_level,
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


class SaveExerciseErrorRequest(BaseModel):
    question: Optional[str] = None
    user_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    exercise_type: Optional[str] = None


@router.post("/api/lessons/{lesson_id}/exercise-error")
async def save_exercise_error(
    lesson_id: int,
    request: SaveExerciseErrorRequest,
    db: Session = Depends(get_db)
):
    """Save a wrong exercise answer to the lesson content for use in next lesson generation."""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    try:
        content = json.loads(lesson.content)
    except Exception:
        content = {}

    errors = content.get("user_exercise_errors", [])
    errors.append({
        "question": request.question,
        "user_answer": request.user_answer,
        "correct_answer": request.correct_answer,
        "type": request.exercise_type or "exercise"
    })
    # Keep last 10 errors only
    content["user_exercise_errors"] = errors[-10:]
    lesson.content = json.dumps(content)
    db.commit()

    return {"success": True, "total_errors": len(content["user_exercise_errors"])}


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
                        "title": future_content.get("title", f"Dzień {future_day}"),
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
            from backend.services.obsidian_service import _folder_name
            folder_id = os.environ.get("GDRIVE_FOLDER_ID")
            subfolder = _folder_name(lesson_data.get("language", ""), lesson_data.get("cefr_level", "A1"))
            url = upload_to_google_drive(filepath, folder_id, subfolder_name=subfolder)
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


@router.get("/api/lessons/history/{user_id}")
async def get_lesson_history(user_id: int, db: Session = Depends(get_db)):
    """Return all lessons for a user ordered by day_number desc, with best test score per day."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    lessons = db.query(Lesson).filter(
        Lesson.user_id == user_id,
        Lesson.language == user.target_language
    ).order_by(Lesson.created_at.desc()).all()

    # Deduplicate: keep only the first (latest) lesson per day_number
    seen_days: set = set()
    deduped = []
    for l in lessons:
        if l.day_number not in seen_days:
            seen_days.add(l.day_number)
            deduped.append(l)
    lessons = sorted(deduped, key=lambda l: l.day_number, reverse=True)

    result = []
    for lesson in lessons:
        # Find best test score for the same calendar day
        lesson_date = lesson.created_at.date() if lesson.created_at else None
        best_score = None
        if lesson_date:
            day_start = datetime.combine(lesson_date, datetime.min.time())
            day_end = datetime.combine(lesson_date + timedelta(days=1), datetime.min.time())
            tests_that_day = db.query(TestResult).filter(
                TestResult.user_id == user_id,
                TestResult.created_at >= day_start,
                TestResult.created_at < day_end,
            ).all()
            if tests_that_day:
                best_score = max(t.score for t in tests_that_day)

        result.append({
            "lesson_id": lesson.id,
            "day_number": lesson.day_number,
            "title": lesson.title,
            "topic": lesson.topic,
            "is_completed": lesson.is_completed,
            "created_at": lesson.created_at.isoformat() if lesson.created_at else None,
            "best_test_score": round(best_score, 1) if best_score is not None else None,
        })

    return {"lessons": result, "total": len(result)}


@router.post("/api/lessons/next/{user_id}")
async def generate_next_lesson(user_id: int, db: Session = Depends(get_db)):
    """Generate the NEXT lesson (max day_number + 1) without deleting the current one."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get active study plan
    study_plan = db.query(StudyPlan).filter(
        StudyPlan.user_id == user_id,
        StudyPlan.is_active == True
    ).first()
    if not study_plan:
        raise HTTPException(status_code=404, detail="No active study plan. Please complete placement test first.")

    study_plan_data = json.loads(study_plan.plan_data)

    # Determine next day number (per-language)
    latest_lesson = db.query(Lesson).filter(
        Lesson.user_id == user_id,
        Lesson.language == user.target_language
    ).order_by(Lesson.day_number.desc()).first()
    next_day = (latest_lesson.day_number + 1) if latest_lesson else 1

    # Get recent errors
    user_errors = get_recent_errors(user_id, db)

    # Get recent topics for interleaving
    week_ago = datetime.combine(date.today() - timedelta(days=7), datetime.min.time())
    recent_lessons = db.query(Lesson).filter(
        Lesson.user_id == user_id,
        Lesson.created_at >= week_ago
    ).order_by(Lesson.created_at.desc()).limit(7).all()
    recent_topics = [l.topic for l in recent_lessons if l.topic] if recent_lessons else None

    # Get exercise errors from recent lessons to pass to prompt
    exercise_errors = []
    if latest_lesson and latest_lesson.content:
        try:
            latest_content = json.loads(latest_lesson.content)
            exercise_errors = latest_content.get("user_exercise_errors", [])
        except Exception:
            pass

    # Generate lesson
    lesson_content = await generate_daily_lesson(
        day_number=next_day,
        study_plan_data=study_plan_data,
        user_errors=user_errors + exercise_errors,
        cefr_level=user.cefr_level,
        language=user.target_language,
        native_language=user.native_language,
        recent_topics=recent_topics
    )

    # Save lesson to DB
    lesson = Lesson(
        user_id=user_id,
        day_number=next_day,
        title=lesson_content.get("title", f"Dzień {next_day}"),
        topic=lesson_content.get("topic", "General"),
        content=json.dumps(lesson_content),
        cefr_level=user.cefr_level,
        language=user.target_language,
        is_completed=False
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)

    # Create flashcards from vocabulary
    vocabulary = lesson_content.get("vocabulary", [])
    for vocab_item in vocabulary:
        word = vocab_item.get("word", "")
        translation = vocab_item.get("translation", "")
        if word and translation:
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
                    cefr_level=user.cefr_level,
                    lesson_id=lesson.id,
                    lesson_day=lesson.day_number,
                    lesson_topic=lesson.topic
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
        "language": lesson.language,
        "cefr_level": lesson.cefr_level,
        "created_at": lesson.created_at.isoformat()
    }


class ExerciseErrorRequest(BaseModel):
    user_id: int
    question: str
    user_answer: str
    correct_answer: str
    exercise_type: Optional[str] = "unknown"


@router.post("/api/lessons/{lesson_id}/exercise-error")
async def record_exercise_error(
    lesson_id: int,
    request: ExerciseErrorRequest,
    db: Session = Depends(get_db)
):
    """Record an exercise error into the lesson's content blob (user_exercise_errors list)."""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    try:
        content = json.loads(lesson.content)
    except Exception:
        content = {}

    errors = content.get("user_exercise_errors", [])
    errors.append({
        "question": request.question,
        "user_answer": request.user_answer,
        "correct_answer": request.correct_answer,
        "exercise_type": request.exercise_type,
    })
    content["user_exercise_errors"] = errors
    lesson.content = json.dumps(content)
    db.commit()

    return {"success": True, "total_errors": len(errors)}


@router.delete("/api/lessons/reset-today/{user_id}")
async def reset_today_lesson(user_id: int, db: Session = Depends(get_db)):
    """Delete today's lesson so it gets regenerated on next visit."""
    today_start = datetime.combine(date.today(), datetime.min.time())
    deleted = db.query(Lesson).filter(
        Lesson.user_id == user_id,
        Lesson.created_at >= today_start
    ).delete()
    db.commit()
    return {"success": True, "deleted": deleted}


@router.post("/api/lessons/{lesson_id}/concept-flashcards")
async def generate_concept_flashcards(lesson_id: int, db: Session = Depends(get_db)):
    """Extract grammar concepts from lesson and create concept flashcards."""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    content = json.loads(lesson.content)
    # lesson content stores grammar as "explanation" (frontend uses content.explanation)
    grammar_explanation = content.get("grammar_explanation") or content.get("explanation", "")
    topic = lesson.topic
    language = lesson.language
    cefr_level = lesson.cefr_level

    if not grammar_explanation:
        return {"success": False, "message": "Brak treści gramatycznej w tej lekcji.", "created": 0}

    # Ask AI to extract key concepts as flashcard pairs
    prompt = f"""From this {language} grammar explanation, extract 3-5 key grammar CONCEPTS as flashcard pairs.
Each flashcard: front = the grammar rule/concept name (in Polish), back = brief explanation + example in {language}.

Grammar topic: {topic}
Explanation: {grammar_explanation[:800]}

Return JSON:
{{
    "concepts": [
        {{
            "front": "Akkusativ z rodzajnikiem określonym",
            "back": "den (m), die (f), das (n), die (pl)\\nBeispiel: Ich sehe den Mann.",
            "example": "Ich sehe den Mann."
        }}
    ]
}}"""

    try:
        result = await ai_generate_json(prompt)
        concepts = result.get("concepts", [])
    except Exception:
        return {"success": False, "message": "AI generation failed", "created": 0}

    created = 0
    skipped = 0
    for concept in concepts:
        front = concept.get("front", "")
        back = concept.get("back", "")
        if not front or not back:
            continue
        # Check if already exists
        existing = db.query(Flashcard).filter(
            Flashcard.user_id == lesson.user_id,
            Flashcard.word == front
        ).first()
        if not existing:
            fc = Flashcard(
                user_id=lesson.user_id,
                word=front,
                translation=back,
                example_sentence=concept.get("example", ""),
                language=language,
                cefr_level=cefr_level
            )
            db.add(fc)
            created += 1
        else:
            skipped += 1

    db.commit()
    if created == 0 and skipped == 0:
        return {"success": False, "message": "AI nie wygenerowało koncepcji dla tej lekcji. Spróbuj ponownie.", "created": 0}
    return {"success": True, "created": created, "skipped": skipped, "total_concepts": len(concepts)}


@router.get("/api/lessons/study-plan/{user_id}")
async def get_study_plan(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    active_plan = db.query(StudyPlan).filter(
        StudyPlan.user_id == user_id,
        StudyPlan.is_active == True
    ).first()

    if not active_plan:
        return {"plan": None, "current_lesson": None}

    import json as _json
    try:
        plan_data = _json.loads(active_plan.plan_data)
    except Exception:
        plan_data = {}

    # Also get current lesson number
    latest_lesson = db.query(Lesson).filter(
        Lesson.user_id == user_id,
        Lesson.language == user.target_language
    ).order_by(Lesson.day_number.desc()).first()

    return {
        "plan": plan_data,
        "current_lesson": latest_lesson.day_number if latest_lesson else 0,
        "cefr_level": active_plan.cefr_level,
        "language": active_plan.language
    }


class EvaluateProductionRequest(BaseModel):
    user_answer: str
    instruction: str
    language: str = "German"
    cefr_level: str = "B1"


@router.post("/api/lessons/{lesson_id}/evaluate-production")
async def evaluate_production_task(
    lesson_id: int,
    request: EvaluateProductionRequest,
    db: Session = Depends(get_db)
):
    if not request.user_answer or not request.user_answer.strip():
        raise HTTPException(status_code=400, detail="Answer cannot be empty")

    prompt = f"""You are a {request.language} language teacher. Evaluate this student's answer.

Level: {request.cefr_level}
Task instruction: {request.instruction}
Student's answer: {request.user_answer}

Evaluate the answer and return ONLY valid JSON:
{{
    "score": 85,
    "feedback": "Detailed feedback in Polish",
    "corrections": [
        {{"error": "mistake in student text", "correction": "correct form"}}
    ],
    "improved_version": "Improved version of their text in {request.language}"
}}

Score 0-100. Corrections array can be empty if there are no errors. Write feedback in Polish."""

    try:
        result = await ai_generate_json(prompt)
        return {
            "success": True,
            "score": result.get("score", 0),
            "feedback": result.get("feedback", ""),
            "corrections": result.get("corrections", []),
            "improved_version": result.get("improved_version", "")
        }
    except Exception as e:
        logger.error(f"Error evaluating production task: {e}")
        return {
            "success": False,
            "score": 0,
            "feedback": "Nie udało się ocenić odpowiedzi. Spróbuj ponownie.",
            "corrections": [],
            "improved_version": ""
        }

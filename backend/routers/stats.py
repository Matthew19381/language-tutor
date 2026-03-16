import csv
import io
import json
import logging
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.models.lesson import Lesson
from backend.models.test_result import TestResult
from backend.models.flashcard import Flashcard
from backend.services.lesson_generator import generate_daily_tips

logger = logging.getLogger(__name__)
router = APIRouter()


def calculate_level(xp: int) -> dict:
    """Calculate user level (1-50) using quadratic curve via achievement_service."""
    from backend.services.achievement_service import calculate_level_from_xp
    return calculate_level_from_xp(xp)


@router.get("/api/stats/{user_id}")
async def get_stats(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get lesson stats
    all_lessons = db.query(Lesson).filter(Lesson.user_id == user_id).all()
    completed_lessons = [l for l in all_lessons if l.is_completed]

    # Get test history
    test_results = db.query(TestResult).filter(
        TestResult.user_id == user_id
    ).order_by(TestResult.created_at.desc()).limit(30).all()

    # Get flashcard stats
    flashcards = db.query(Flashcard).filter(
        Flashcard.user_id == user_id,
        Flashcard.is_active == True
    ).all()

    now = datetime.utcnow()
    due_flashcards = [f for f in flashcards if f.next_review_date and f.next_review_date <= now]

    # Calculate streaks
    streak = 0
    if completed_lessons:
        lesson_dates = sorted(set(l.completed_at.date() for l in completed_lessons if l.completed_at))
        if lesson_dates:
            streak = 1
            for i in range(len(lesson_dates) - 1, 0, -1):
                if (lesson_dates[i] - lesson_dates[i - 1]).days == 1:
                    streak += 1
                else:
                    break

    # Calculate error categories
    error_categories = {}
    for test in test_results:
        if test.errors:
            try:
                errors = json.loads(test.errors)
                for error in errors:
                    error_type = error.get("type", "unknown")
                    error_categories[error_type] = error_categories.get(error_type, 0) + 1
            except Exception:
                pass

    # Test history for chart
    test_history_chart = []
    for result in reversed(test_results[:14]):  # Last 14 tests
        test_history_chart.append({
            "date": result.created_at.strftime("%m/%d"),
            "score": round(result.score, 1),
            "type": result.test_type
        })

    # Lesson completion history
    lesson_history = []
    for lesson in sorted(all_lessons, key=lambda x: x.day_number)[-14:]:
        lesson_history.append({
            "day": lesson.day_number,
            "title": lesson.title,
            "completed": lesson.is_completed,
            "date": lesson.created_at.strftime("%m/%d")
        })

    level_info = calculate_level(user.total_xp)

    from backend.services.achievement_service import get_all_achievements_for_user, get_unnotified_achievements
    achievements_data = get_all_achievements_for_user(user_id, db)
    unnotified = get_unnotified_achievements(user_id, db)

    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "native_language": user.native_language,
            "target_language": user.target_language,
            "cefr_level": user.cefr_level,
            "streak_days": streak,
            "total_xp": user.total_xp,
            "member_since": user.created_at.strftime("%B %d, %Y") if user.created_at else "Unknown"
        },
        "level_info": level_info,
        "lessons": {
            "total": len(all_lessons),
            "completed": len(completed_lessons),
            "completion_rate": round(len(completed_lessons) / len(all_lessons) * 100, 1) if all_lessons else 0,
            "history": lesson_history
        },
        "tests": {
            "total_taken": len(test_results),
            "average_score": round(sum(t.score for t in test_results) / len(test_results), 1) if test_results else 0,
            "best_score": round(max(t.score for t in test_results), 1) if test_results else 0,
            "history": test_history_chart
        },
        "flashcards": {
            "total": len(flashcards),
            "due_today": len(due_flashcards)
        },
        "error_categories": error_categories,
        "achievements": achievements_data,
        "new_achievements": unnotified,
    }


class AddXPRequest(BaseModel):
    amount: int
    reason: Optional[str] = "activity"


@router.post("/api/stats/{user_id}/xp")
async def add_xp(
    user_id: int,
    request: AddXPRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.total_xp += request.amount
    db.commit()

    level_info = calculate_level(user.total_xp)

    return {
        "success": True,
        "xp_added": request.amount,
        "total_xp": user.total_xp,
        "level_info": level_info,
        "reason": request.reason
    }


@router.get("/api/tips/{user_id}")
async def get_daily_tips(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        tips = await generate_daily_tips(
            cefr_level=user.cefr_level,
            language=user.target_language,
            native_language=user.native_language
        )
        return {
            "success": True,
            "user_id": user_id,
            "cefr_level": user.cefr_level,
            "language": user.target_language,
            "tips": tips.get("tips", [])
        }
    except Exception as e:
        logger.error(f"Error getting daily tips: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/stats/{user_id}/leaderboard")
async def get_leaderboard_position(user_id: int, db: Session = Depends(get_db)):
    """Get the user's position among all users by XP."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all users sorted by XP
    all_users = db.query(User).order_by(User.total_xp.desc()).all()
    position = next((i + 1 for i, u in enumerate(all_users) if u.id == user_id), 1)

    return {
        "user_id": user_id,
        "position": position,
        "total_users": len(all_users),
        "xp": user.total_xp,
        "top_users": [
            {
                "name": u.name,
                "xp": u.total_xp,
                "cefr_level": u.cefr_level
            }
            for u in all_users[:5]
        ]
    }


@router.get("/api/stats/{user_id}/export-csv")
async def export_progress_csv(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    lessons = db.query(Lesson).filter(Lesson.user_id == user_id).order_by(Lesson.created_at.asc()).all()
    test_results = db.query(TestResult).filter(TestResult.user_id == user_id).order_by(TestResult.created_at.asc()).all()
    flashcards = db.query(Flashcard).filter(Flashcard.user_id == user_id).all()

    # Build test results lookup by date
    tests_by_date = {}
    for t in test_results:
        d = t.created_at.strftime("%Y-%m-%d")
        if d not in tests_by_date:
            tests_by_date[d] = []
        tests_by_date[d].append(round(t.score, 1))

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "day_number", "lesson_title", "lesson_completed", "test_scores", "xp_total", "streak", "flashcard_count"])

    # Calculate cumulative XP per lesson completion
    xp = 0
    streak = 0
    lesson_dates = sorted(set(l.completed_at.date() for l in lessons if l.completed_at))

    for lesson in lessons:
        d = lesson.created_at.strftime("%Y-%m-%d")
        if lesson.is_completed:
            xp += 25
            # Approximate streak at time of completion
            if lesson.completed_at:
                streak = sum(
                    1 for ld in lesson_dates
                    if ld <= lesson.completed_at.date()
                )
        scores = tests_by_date.get(d, [])
        scores_str = ";".join(str(s) for s in scores) if scores else ""
        writer.writerow([
            d,
            lesson.day_number,
            lesson.title,
            lesson.is_completed,
            scores_str,
            xp,
            streak,
            len(flashcards),
        ])

    output.seek(0)
    filename = f"progress_{user.name}_{date.today().isoformat()}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

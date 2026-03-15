import json
import logging
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.models.lesson import Lesson
from backend.models.test_result import TestResult
from backend.models.study_plan import StudyPlan
from backend.services.test_generator import (
    get_or_create_daily_test,
    submit_test,
    get_or_create_weekly_test,
    get_test_history
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/tests/daily/{user_id}")
async def get_daily_test(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Find today's lesson
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_lesson = db.query(Lesson).filter(
        Lesson.user_id == user_id,
        Lesson.created_at >= today_start
    ).first()

    if not today_lesson:
        raise HTTPException(
            status_code=404,
            detail="No lesson found for today. Please complete today's lesson first."
        )

    lesson_content = json.loads(today_lesson.content)

    try:
        test_data = await get_or_create_daily_test(user_id, lesson_content, db)
        return {
            "success": True,
            "lesson_id": today_lesson.id,
            "lesson_title": today_lesson.title,
            **test_data
        }
    except Exception as e:
        logger.error(f"Error getting daily test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class SubmitTestRequest(BaseModel):
    user_id: int
    test_type: str = "daily"
    questions: list
    answers: dict


@router.post("/api/tests/submit")
async def submit_test_answers(
    request: SubmitTestRequest,
    db: Session = Depends(get_db)
):
    try:
        result = await submit_test(
            user_id=request.user_id,
            test_type=request.test_type,
            questions=request.questions,
            answers=request.answers,
            db=db
        )
        # Check achievements after test
        from backend.services.achievement_service import check_and_award_achievements
        user = db.query(User).filter(User.id == request.user_id).first()
        newly_awarded = []
        if user:
            newly_awarded = check_and_award_achievements(user, db)
        return {
            "success": True,
            "new_achievements": newly_awarded,
            **result
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/tests/weekly/{user_id}")
async def get_weekly_test(
    user_id: int,
    week: Optional[int] = None,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if week is None:
        # Calculate current week number
        if user.created_at:
            days_elapsed = (date.today() - user.created_at.date()).days
            week = (days_elapsed // 7) + 1
        else:
            week = 1

    try:
        test_data = await get_or_create_weekly_test(user_id, week, db)
        return {
            "success": True,
            **test_data
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting weekly test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/tests/history/{user_id}")
async def get_history(
    user_id: int,
    limit: Optional[int] = 20,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    history = get_test_history(user_id, db, limit)

    # Calculate stats
    if history:
        avg_score = sum(h["score"] for h in history) / len(history)
        best_score = max(h["score"] for h in history)
        total_tests = len(history)
    else:
        avg_score = 0
        best_score = 0
        total_tests = 0

    return {
        "history": history,
        "stats": {
            "total_tests": total_tests,
            "average_score": round(avg_score, 1),
            "best_score": round(best_score, 1)
        }
    }


@router.get("/api/tests/result/{result_id}")
async def get_test_result(result_id: int, db: Session = Depends(get_db)):
    result = db.query(TestResult).filter(TestResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Test result not found")

    errors = json.loads(result.errors) if result.errors else []
    answers = json.loads(result.answers) if result.answers else {}

    return {
        "id": result.id,
        "user_id": result.user_id,
        "test_type": result.test_type,
        "score": result.score,
        "answers": answers,
        "errors": errors,
        "cefr_level": result.cefr_level,
        "language": result.language,
        "created_at": result.created_at.isoformat()
    }

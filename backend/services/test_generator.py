import json
import logging
from sqlalchemy.orm import Session
from backend.models.test_result import TestResult
from backend.models.user import User
from backend.services.lesson_generator import (
    generate_daily_test,
    generate_weekly_test,
    analyze_test_errors
)

logger = logging.getLogger(__name__)


async def get_or_create_daily_test(user_id: int, lesson_content: dict, db: Session) -> dict:
    """Get or generate a daily test for a user."""
    from backend.models.lesson import Lesson
    from datetime import datetime, date

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found")

    # Check if there's already a daily test for today
    today_start = datetime.combine(date.today(), datetime.min.time())
    existing_test = db.query(TestResult).filter(
        TestResult.user_id == user_id,
        TestResult.test_type == "daily",
        TestResult.created_at >= today_start
    ).first()

    if existing_test:
        return {
            "test_id": existing_test.id,
            "already_taken": True,
            "score": existing_test.score,
            "questions": json.loads(existing_test.answers) if existing_test.answers else []
        }

    # Generate new test from lesson content
    test_data = await generate_daily_test(
        lesson_content=lesson_content,
        cefr_level=user.cefr_level,
        language=user.target_language,
        native_language=user.native_language
    )

    return {
        "test_id": None,
        "already_taken": False,
        "questions": test_data.get("questions", []),
        "cefr_level": user.cefr_level,
        "language": user.target_language
    }


async def submit_test(
    user_id: int,
    test_type: str,
    questions: list,
    answers: dict,
    db: Session
) -> dict:
    """Submit test answers, analyze errors, save to DB, return results."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found")

    # Analyze errors
    analysis = await analyze_test_errors(
        questions=questions,
        answers=answers,
        language=user.target_language,
        native_language=user.native_language
    )

    score = analysis.get("score", 0)
    errors = analysis.get("errors", [])

    # Save test result to DB
    test_result = TestResult(
        user_id=user_id,
        test_type=test_type,
        score=score,
        answers=json.dumps(answers),
        errors=json.dumps(errors),
        cefr_level=user.cefr_level,
        language=user.target_language
    )
    db.add(test_result)

    # Award XP based on score
    xp_earned = int(score * 0.5)  # Max 50 XP per test
    user.total_xp += xp_earned

    db.commit()
    db.refresh(test_result)

    return {
        "test_result_id": test_result.id,
        "score": score,
        "errors": errors,
        "performance_summary": analysis.get("performance_summary", ""),
        "xp_earned": xp_earned
    }


async def get_or_create_weekly_test(user_id: int, week_number: int, db: Session) -> dict:
    """Get or generate a weekly test."""
    from backend.models.study_plan import StudyPlan

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found")

    # Get active study plan
    study_plan = db.query(StudyPlan).filter(
        StudyPlan.user_id == user_id,
        StudyPlan.is_active == True
    ).first()

    if not study_plan:
        raise ValueError("No active study plan found")

    study_plan_data = json.loads(study_plan.plan_data)

    # Generate weekly test
    test_data = await generate_weekly_test(
        study_plan_data=study_plan_data,
        week_number=week_number,
        cefr_level=user.cefr_level,
        language=user.target_language,
        native_language=user.native_language
    )

    return {
        "week_number": week_number,
        "questions": test_data.get("questions", []),
        "cefr_level": user.cefr_level,
        "language": user.target_language
    }


def calculate_score(questions: list, answers: dict) -> float:
    """Calculate test score from questions and answers."""
    total_points = sum(q.get("points", 10) for q in questions)
    if total_points == 0:
        return 0.0

    earned_points = 0
    for q in questions:
        user_ans = answers.get(str(q["id"]), answers.get(q["id"], ""))
        if str(user_ans).upper().strip() == str(q["correct"]).upper().strip():
            earned_points += q.get("points", 10)

    return (earned_points / total_points) * 100


def get_test_history(user_id: int, db: Session, limit: int = 20) -> list:
    """Get test history for a user."""
    results = db.query(TestResult).filter(
        TestResult.user_id == user_id
    ).order_by(TestResult.created_at.desc()).limit(limit).all()

    history = []
    for result in results:
        history.append({
            "id": result.id,
            "test_type": result.test_type,
            "score": result.score,
            "cefr_level": result.cefr_level,
            "created_at": result.created_at.isoformat(),
            "errors_count": len(json.loads(result.errors)) if result.errors else 0
        })

    return history

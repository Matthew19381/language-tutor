import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.models.test_result import TestResult
from backend.models.study_plan import StudyPlan
from backend.models.flashcard import Flashcard
from backend.services.lesson_generator import (
    generate_placement_test,
    analyze_placement_results,
    generate_study_plan
)
from backend.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class StartPlacementRequest(BaseModel):
    user_id: Optional[int] = None
    language: Optional[str] = None
    native_language: Optional[str] = None


class SubmitPlacementRequest(BaseModel):
    user_id: Optional[int] = None
    questions: list
    answers: dict
    language: Optional[str] = None
    native_language: Optional[str] = None


class CreateUserRequest(BaseModel):
    name: str
    native_language: Optional[str] = None
    target_language: Optional[str] = None


@router.post("/api/placement/start")
async def start_placement(
    request: StartPlacementRequest,
    db: Session = Depends(get_db)
):
    language = request.language or settings.TARGET_LANGUAGE
    native_language = request.native_language or settings.NATIVE_LANGUAGE

    try:
        test_data = await generate_placement_test(language, native_language)
        return {
            "success": True,
            "language": language,
            "native_language": native_language,
            "questions": test_data.get("questions", []),
            "total_questions": len(test_data.get("questions", []))
        }
    except Exception as e:
        logger.error(f"Error starting placement test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/placement/submit")
async def submit_placement(
    request: SubmitPlacementRequest,
    db: Session = Depends(get_db)
):
    language = request.language or settings.TARGET_LANGUAGE
    native_language = request.native_language or settings.NATIVE_LANGUAGE

    try:
        # Analyze results
        analysis = await analyze_placement_results(
            questions=request.questions,
            answers=request.answers,
            language=language
        )

        cefr_level = analysis.get("cefr_level", "A1")
        score = analysis.get("score", 0)

        user = None
        study_plan_data = None

        if request.user_id:
            user = db.query(User).filter(User.id == request.user_id).first()
            if user:
                # Update user's CEFR level
                user.cefr_level = cefr_level
                db.commit()

                # Save test result
                test_result = TestResult(
                    user_id=user.id,
                    test_type="placement",
                    score=score,
                    answers=json.dumps(request.answers),
                    errors=json.dumps(analysis.get("weak_areas", [])),
                    cefr_level=cefr_level,
                    language=language
                )
                db.add(test_result)

                # Generate study plan
                user_data = {
                    "name": user.name,
                    "cefr_level": cefr_level,
                    "native_language": native_language,
                    "target_language": language
                }
                study_plan_data = await generate_study_plan(user_data, language, native_language)

                # Deactivate old study plans
                db.query(StudyPlan).filter(
                    StudyPlan.user_id == user.id,
                    StudyPlan.is_active == True
                ).update({"is_active": False})

                # Save new study plan
                new_plan = StudyPlan(
                    user_id=user.id,
                    language=language,
                    cefr_level=cefr_level,
                    plan_data=json.dumps(study_plan_data),
                    is_active=True
                )
                db.add(new_plan)
                db.commit()

        return {
            "success": True,
            "cefr_level": cefr_level,
            "score": score,
            "strong_areas": analysis.get("strong_areas", []),
            "weak_areas": analysis.get("weak_areas", []),
            "recommendations": analysis.get("recommendations", ""),
            "study_plan": study_plan_data
        }
    except Exception as e:
        logger.error(f"Error submitting placement test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/placement/create-user")
async def create_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db)
):
    try:
        native_language = request.native_language or settings.NATIVE_LANGUAGE
        target_language = request.target_language or settings.TARGET_LANGUAGE

        user = User(
            name=request.name,
            native_language=native_language,
            target_language=target_language,
            cefr_level="A1",
            streak_days=0,
            total_xp=0
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "success": True,
            "user_id": user.id,
            "name": user.name,
            "native_language": user.native_language,
            "target_language": user.target_language,
            "cefr_level": user.cefr_level
        }
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/placement/user/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.id,
        "name": user.name,
        "native_language": user.native_language,
        "target_language": user.target_language,
        "cefr_level": user.cefr_level,
        "streak_days": user.streak_days,
        "total_xp": user.total_xp,
        "created_at": user.created_at.isoformat()
    }

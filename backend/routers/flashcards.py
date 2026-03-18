import logging
import os
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.models.flashcard import Flashcard
from backend.services.anki_service import generate_anki_deck
from backend.services.audio_service import generate_flashcard_audio
from backend.services.gemini_service import generate_json

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/flashcards/{user_id}")
async def get_flashcards(
    user_id: int,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query = db.query(Flashcard).filter(Flashcard.user_id == user_id)
    if active_only:
        query = query.filter(Flashcard.is_active == True)

    flashcards = query.order_by(Flashcard.created_at.desc()).all()

    return {
        "flashcards": [
            {
                "id": f.id,
                "word": f.word,
                "translation": f.translation,
                "example_sentence": f.example_sentence,
                "audio_path": f.audio_path,
                "language": f.language,
                "cefr_level": f.cefr_level,
                "ease_factor": f.ease_factor,
                "interval_days": f.interval_days,
                "next_review_date": f.next_review_date.isoformat() if f.next_review_date else None,
                "created_at": f.created_at.isoformat(),
                "lesson_id": f.lesson_id,
                "lesson_day": f.lesson_day,
                "lesson_topic": f.lesson_topic,
            }
            for f in flashcards
        ],
        "total": len(flashcards)
    }


@router.get("/api/flashcards/{user_id}/due")
async def get_due_flashcards(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.utcnow()
    due_cards = db.query(Flashcard).filter(
        Flashcard.user_id == user_id,
        Flashcard.is_active == True,
        Flashcard.next_review_date <= now
    ).order_by(Flashcard.next_review_date.asc()).all()

    return {
        "due_cards": [
            {
                "id": f.id,
                "word": f.word,
                "translation": f.translation,
                "example_sentence": f.example_sentence,
                "audio_path": f.audio_path,
                "ease_factor": f.ease_factor,
                "interval_days": f.interval_days
            }
            for f in due_cards
        ],
        "count": len(due_cards)
    }


class ReviewFlashcardRequest(BaseModel):
    rating: int  # 1=Again, 2=Hard, 3=Good, 4=Easy (SM-2 ratings)


@router.post("/api/flashcards/{flashcard_id}/review")
async def review_flashcard(
    flashcard_id: int,
    request: ReviewFlashcardRequest,
    db: Session = Depends(get_db)
):
    flashcard = db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    # SM-2 algorithm implementation
    rating = request.rating  # 1-4 scale
    ef = flashcard.ease_factor
    interval = flashcard.interval_days

    if rating == 1:  # Again
        interval = 1
        ef = max(1.3, ef - 0.2)
    elif rating == 2:  # Hard
        interval = max(1, int(interval * 1.2))
        ef = max(1.3, ef - 0.15)
    elif rating == 3:  # Good
        if interval == 1:
            interval = 3
        elif interval <= 3:
            interval = 7
        else:
            interval = int(interval * ef)
    elif rating == 4:  # Easy
        if interval == 1:
            interval = 4
        elif interval <= 4:
            interval = 10
        else:
            interval = int(interval * ef * 1.3)
        ef = min(2.5, ef + 0.15)

    # Update flashcard
    flashcard.ease_factor = round(ef, 2)
    flashcard.interval_days = interval
    flashcard.next_review_date = datetime.fromtimestamp(
        datetime.utcnow().timestamp() + (interval * 86400)
    )

    db.commit()

    return {
        "success": True,
        "flashcard_id": flashcard_id,
        "new_interval": interval,
        "new_ease_factor": round(ef, 2),
        "next_review": flashcard.next_review_date.isoformat()
    }


@router.post("/api/flashcards/{user_id}/export-anki")
async def export_anki(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    flashcards = db.query(Flashcard).filter(
        Flashcard.user_id == user_id,
        Flashcard.is_active == True
    ).all()

    if not flashcards:
        raise HTTPException(status_code=404, detail="No flashcards found to export")

    try:
        deck_path = generate_anki_deck(
            flashcards=flashcards,
            language=user.target_language,
            user_name=user.name
        )

        return FileResponse(
            path=deck_path,
            filename=os.path.basename(deck_path),
            media_type="application/octet-stream"
        )
    except Exception as e:
        logger.error(f"Error exporting Anki deck: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating Anki deck: {str(e)}")


@router.post("/api/flashcards/{flashcard_id}/audio")
async def generate_audio(flashcard_id: int, db: Session = Depends(get_db)):
    flashcard = db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    try:
        audio_path = await generate_flashcard_audio(
            word=flashcard.word,
            language=flashcard.language,
            flashcard_id=flashcard_id
        )
        if audio_path:
            flashcard.audio_path = audio_path
            db.commit()

        return {"success": True, "audio_path": audio_path}
    except Exception as e:
        logger.error(f"Error generating flashcard audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class AddFlashcardRequest(BaseModel):
    word: str
    translation: str
    example_sentence: Optional[str] = None


@router.post("/api/flashcards/{user_id}/add")
async def add_flashcard(
    user_id: int,
    request: AddFlashcardRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check for duplicate
    existing = db.query(Flashcard).filter(
        Flashcard.user_id == user_id,
        Flashcard.word == request.word
    ).first()

    if existing:
        return {"success": False, "message": f"Fiszka '{request.word}' już istnieje w Twojej kolekcji.", "id": existing.id}

    flashcard = Flashcard(
        user_id=user_id,
        word=request.word,
        translation=request.translation,
        example_sentence=request.example_sentence,
        language=user.target_language,
        cefr_level=user.cefr_level
    )
    db.add(flashcard)
    db.commit()
    db.refresh(flashcard)

    return {"success": True, "id": flashcard.id, "message": "Flashcard added successfully"}


class AddFlashcardAIRequest(BaseModel):
    word: str


@router.post("/api/flashcards/{user_id}/add-ai")
async def add_flashcard_ai(
    user_id: int,
    request: AddFlashcardAIRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check for duplicate
    existing = db.query(Flashcard).filter(
        Flashcard.user_id == user_id,
        Flashcard.word == request.word
    ).first()

    if existing:
        return {"success": False, "message": f"Fiszka '{request.word}' już istnieje w Twojej kolekcji.", "id": existing.id}

    # Use AI to generate translation and example
    prompt = f"""Given the {user.target_language} word or phrase '{request.word}', provide:
- ONE main Polish translation (the most common/primary meaning only — do NOT list all conjugated forms)
- An example sentence in {user.target_language} (at {user.cefr_level} level)
- Polish translation of that example sentence

Return ONLY valid JSON:
{{
    "translation": "single main Polish translation",
    "example": "Example sentence in {user.target_language}",
    "example_translation": "Polish translation of the example"
}}"""

    translation = ""
    example = ""
    try:
        ai_result = await generate_json(prompt)
        # Handle both direct dict and nested formats
        if isinstance(ai_result, dict):
            translation = (
                ai_result.get("translation") or
                ai_result.get("polish_translation") or
                ai_result.get("meaning") or ""
            )
            example = (
                ai_result.get("example") or
                ai_result.get("example_sentence") or
                ai_result.get("sentence") or ""
            )
            # If translation is a dict (nested), try to extract string
            if isinstance(translation, dict):
                translation = translation.get("polish", "") or str(translation)
            if isinstance(example, dict):
                example = example.get("sentence", "") or str(example)
            translation = str(translation).strip()
            example = str(example).strip()
    except Exception as e:
        logger.warning(f"AI flashcard generation failed: {e}")
        translation = ""
        example = ""

    flashcard = Flashcard(
        user_id=user_id,
        word=request.word,
        translation=translation,
        example_sentence=example,
        language=user.target_language,
        cefr_level=user.cefr_level
    )
    db.add(flashcard)
    db.commit()
    db.refresh(flashcard)

    return {
        "success": True,
        "id": flashcard.id,
        "word": flashcard.word,
        "translation": translation,
        "example": example,
        "message": "Flashcard added with AI"
    }

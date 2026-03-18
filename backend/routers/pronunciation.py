import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User

try:
    from backend.services.pronunciation_service import transcribe_audio, score_pronunciation
    PRONUNCIATION_AVAILABLE = True
except Exception:
    PRONUNCIATION_AVAILABLE = False
    transcribe_audio = None
    score_pronunciation = None

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/api/pronunciation/analyze")
async def analyze_pronunciation(
    audio: UploadFile = File(...),
    target_text: str = Form(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db),
):
    """Transcribe uploaded audio and compare to target_text. Returns pronunciation score."""
    if not PRONUNCIATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Pronunciation service unavailable: faster-whisper not installed.")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file received.")

    # Determine format from content type or filename
    content_type = audio.content_type or ""
    filename = audio.filename or ""
    if "webm" in content_type or "webm" in filename:
        fmt = "webm"
    elif "ogg" in content_type or "ogg" in filename:
        fmt = "ogg"
    elif "mp4" in content_type or "m4a" in filename:
        fmt = "mp4"
    elif "wav" in content_type or "wav" in filename:
        fmt = "wav"
    else:
        fmt = "webm"  # default for MediaRecorder

    try:
        transcribed = transcribe_audio(audio_bytes, audio_format=fmt)
        result = score_pronunciation(transcribed, target_text)
        result["language"] = user.target_language
        return {"success": True, **result}
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="Pronunciation service unavailable. Please run: pip install faster-whisper==1.0.3"
        )
    except Exception as e:
        logger.error(f"Pronunciation analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/pronunciation/phrases/{user_id}")
async def get_practice_phrases(user_id: int, db: Session = Depends(get_db)):
    """Return practice phrases from the user's recent lessons."""
    from backend.models.lesson import Lesson
    import json
    from datetime import datetime, date, timedelta

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get phrases from last 7 days of lessons
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_lessons = db.query(Lesson).filter(
        Lesson.user_id == user_id,
        Lesson.created_at >= week_ago
    ).order_by(Lesson.created_at.desc()).limit(3).all()

    phrases = []
    for lesson in recent_lessons:
        try:
            content = json.loads(lesson.content)
            # Get vocabulary words
            for vocab in content.get("vocabulary", [])[:3]:
                word = vocab.get("word", "")
                example = vocab.get("example", "")
                if example:
                    phrases.append({"text": example, "source": f"Vocabulary: {word}"})
                elif word:
                    phrases.append({"text": word, "source": "Vocabulary"})
            # Get dialogue lines
            for line in content.get("dialogue", {}).get("lines", [])[:2]:
                text = line.get("text", "")
                if text:
                    phrases.append({"text": text, "source": f"Dialogue (Speaker {line.get('speaker', '?')})"})
        except Exception:
            pass

    if not phrases:
        phrases = [
            {"text": "Hallo, wie geht es dir?", "source": "Basic phrases"},
            {"text": "Ich lerne gerade Deutsch.", "source": "Basic phrases"},
            {"text": "Können Sie mir bitte helfen?", "source": "Basic phrases"},
        ]

    return {
        "language": user.target_language,
        "phrases": phrases[:10],
    }

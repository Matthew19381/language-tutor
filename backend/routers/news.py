import logging
import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.services.news_service import get_news_for_user

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory cache: key = (user_id, language) -> {"timestamp": float, "data": list}
_news_cache: dict = {}
CACHE_TTL_SECONDS = 6 * 3600  # 6 hours


@router.get("/api/news/{user_id}")
async def get_news(user_id: int, limit: int = 5, db: Session = Depends(get_db)):
    """Fetch and simplify news articles for the user's target language and CEFR level."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cache_key = (user_id, user.target_language)
    now = time.time()
    cached = _news_cache.get(cache_key)
    if cached and (now - cached["timestamp"]) < CACHE_TTL_SECONDS:
        logger.info(f"Returning cached news for user {user_id} / {user.target_language}")
        return {
            "success": True,
            "language": user.target_language,
            "cefr_level": user.cefr_level,
            "articles": cached["data"],
            "cached": True,
        }

    try:
        articles = await get_news_for_user(
            language=user.target_language,
            cefr_level=user.cefr_level,
            native_language=user.native_language,
            limit=min(limit, 8),
        )
        _news_cache[cache_key] = {"timestamp": now, "data": articles}
        return {
            "success": True,
            "language": user.target_language,
            "cefr_level": user.cefr_level,
            "articles": articles,
            "cached": False,
        }
    except Exception as e:
        logger.error(f"Error fetching news for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

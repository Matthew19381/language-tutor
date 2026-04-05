import json
import logging
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.models.lesson import Lesson
from backend.config import settings
from backend.services.gemini_service import generate_json

logger = logging.getLogger(__name__)
router = APIRouter()

LANG_TO_RELEVANCE = {
    "German": "de",
    "English": "en",
    "Spanish": "es",
    "Russian": "ru",
    "Chinese": "zh-Hans",
}

CEFR_DESCRIPTIONS = {
    "A1": "bardzo wolna mowa, krótkie zdania, absolutny początkujący",
    "A2": "prosta mowa, codzienne tematy, elementarny poziom",
    "B1": "średnie tempo, codzienne rozmowy, poziom średnio-zaawansowany",
    "B2": "naturalne tempo mówców native, różne tematy",
    "C1": "zaawansowany, złożone tematy, autentyczne materiały",
    "C2": "biegły, dowolne autentyczne treści",
}


def _extract_lesson_context(lesson: Lesson) -> dict:
    """Pull topic, title, and top vocabulary words from a lesson."""
    topic = lesson.topic or ""
    title = lesson.title or ""
    vocab_words = []
    try:
        content = json.loads(lesson.content)
        vocab = content.get("vocabulary", [])
        vocab_words = [v.get("word", "") for v in vocab[:8] if v.get("word")]
    except Exception:
        pass
    return {"topic": topic, "title": title, "vocab": vocab_words}


async def _suggest_queries(
    language: str,
    cefr_level: str,
    native_language: str,
    lesson_context: dict | None = None,
) -> list[str]:
    cefr_desc = CEFR_DESCRIPTIONS.get(cefr_level, "")

    if lesson_context:
        topic = lesson_context.get("topic", "")
        title = lesson_context.get("title", "")
        vocab = lesson_context.get("vocab", [])
        vocab_str = ", ".join(vocab) if vocab else "brak"

        prompt = f"""Pomagasz osobie mówiącej po {native_language} uczyć się {language} na poziomie CEFR {cefr_level}.

Dzisiejsza lekcja:
- Tytuł: {title}
- Temat: {topic}
- Słownictwo z lekcji: {vocab_str}

Zaproponuj 6 zapytań do YouTube które:
1. Pierwsze 3 są BEZPOŚREDNIO powiązane z tematem lekcji ("{topic}") — szukaj filmów po {language} NA TEN KONKRETNY TEMAT
2. Następne 3 są ogólne ale dostosowane do poziomu {cefr_level} ({cefr_desc}) w języku {language}

Ważne:
- Filmy mają być MÓWIONE po {language} (nie z napisami)
- Zapytania po angielsku lub w języku {language}
- Dla A1/A2: wolna mowa, lektor, kanały edukacyjne
- Dla B1+: autentyczne treści (vlogi, podcasty, wiadomości)

Zwróć JSON:
{{"queries": ["query1", "query2", "query3", "query4", "query5", "query6"],
  "topic_queries": [0, 1, 2]}}

Przykłady dla German B1, temat "Wohnung mieten" (wynajmowanie mieszkania):
queries: ["Wohnung mieten Deutschland Tipps", "Mietvertrag erklärung Deutsch", "Wohnungssuche Berlin Vlog", "Deutsch B1 Alltag", "Deutsche Gespräche B1", "Deutsch lernen Alltag"]"""
    else:
        prompt = f"""Pomagasz osobie mówiącej po {native_language} uczyć się {language} na poziomie CEFR {cefr_level} ({cefr_desc}).

Zaproponuj 6 zapytań YouTube do nauki {language}. Filmy mają być MÓWIONE po {language}.
Dla {cefr_level}: {cefr_desc}.

Zwróć JSON:
{{"queries": ["q1", "q2", "q3", "q4", "q5", "q6"], "topic_queries": []}}"""

    try:
        result = await generate_json(prompt)
        return result.get("queries", []), result.get("topic_queries", [])
    except Exception:
        fallback = {
            "A1": [f"{language} für Anfänger langsam", f"easy {language} A1 slow", f"learn {language} beginners"],
            "A2": [f"einfaches {language} A2", f"easy {language} conversation A2"],
            "B1": [f"{language} B1 Alltag", f"{language} intermediate listening"],
            "B2": [f"{language} Nachrichten einfach", f"{language} podcast B2"],
            "C1": [f"{language} Dokumentation", f"authentic {language} content C1"],
            "C2": [f"{language} Literatur", f"native {language} speakers"],
        }
        return fallback.get(cefr_level, [f"learn {language}"]), []


async def _search_youtube(query: str, language_code: str, max_results: int = 6) -> list[dict]:
    if not settings.YOUTUBE_API_KEY:
        raise HTTPException(status_code=503, detail="Brak klucza YouTube API")

    params = {
        "key": settings.YOUTUBE_API_KEY,
        "q": query,
        "part": "snippet",
        "type": "video",
        "maxResults": max_results,
        "relevanceLanguage": language_code,
        "videoEmbeddable": "true",
        "safeSearch": "moderate",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get("https://www.googleapis.com/youtube/v3/search", params=params)
        if resp.status_code != 200:
            logger.error(f"YouTube API error: {resp.status_code} {resp.text}")
            raise HTTPException(status_code=502, detail="Błąd YouTube API")
        data = resp.json()

    videos = []
    for item in data.get("items", []):
        vid_id = item.get("id", {}).get("videoId")
        snippet = item.get("snippet", {})
        if not vid_id:
            continue
        videos.append({
            "video_id": vid_id,
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "description": snippet.get("description", "")[:200],
            "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
            "published_at": snippet.get("publishedAt", "")[:10],
            "url": f"https://www.youtube.com/watch?v={vid_id}",
        })
    return videos


@router.get("/api/youtube/search")
async def search_videos(
    user_id: int,
    query: str = Query(default=""),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    language = user.target_language
    cefr_level = user.cefr_level
    native_language = user.native_language
    lang_code = LANG_TO_RELEVANCE.get(language, "en")

    try:
        if query.strip():
            videos = await _search_youtube(f"{query} {language}", lang_code)
            return {
                "videos": videos,
                "query_used": query,
                "suggested": False,
            }

        # Get most recent lesson for topic context
        latest_lesson = (
            db.query(Lesson)
            .filter(Lesson.user_id == user_id, Lesson.language == language)
            .order_by(Lesson.created_at.desc())
            .first()
        )
        lesson_context = _extract_lesson_context(latest_lesson) if latest_lesson else None

        queries, topic_query_indices = await _suggest_queries(
            language, cefr_level, native_language, lesson_context
        )
        if not queries:
            queries = [f"learn {language} {cefr_level}"]

        # Fetch topic-related videos first (higher priority), then general
        topic_videos = []
        general_videos = []
        seen_ids = set()

        topic_qs = [queries[i] for i in topic_query_indices if i < len(queries)]
        general_qs = [q for i, q in enumerate(queries) if i not in topic_query_indices]

        if topic_qs:
            results = await _search_youtube(topic_qs[0], lang_code, max_results=5)
            for v in results:
                if v["video_id"] not in seen_ids:
                    topic_videos.append({**v, "is_lesson_related": True})
                    seen_ids.add(v["video_id"])

        if general_qs:
            results = await _search_youtube(general_qs[0], lang_code, max_results=6)
            for v in results:
                if v["video_id"] not in seen_ids:
                    general_videos.append({**v, "is_lesson_related": False})
                    seen_ids.add(v["video_id"])

        # Fill up if not enough
        if len(topic_videos) + len(general_videos) < 4 and len(general_qs) > 1:
            extra = await _search_youtube(general_qs[1], lang_code, max_results=4)
            for v in extra:
                if v["video_id"] not in seen_ids:
                    general_videos.append({**v, "is_lesson_related": False})
                    seen_ids.add(v["video_id"])

        all_videos = topic_videos + general_videos

        return {
            "videos": all_videos,
            "query_used": topic_qs[0] if topic_qs else (general_qs[0] if general_qs else ""),
            "suggested_queries": queries,
            "topic_queries": topic_qs,
            "suggested": True,
            "cefr_level": cefr_level,
            "language": language,
            "lesson_topic": lesson_context.get("topic") if lesson_context else None,
            "lesson_title": lesson_context.get("title") if lesson_context else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("YouTube search error")
        raise HTTPException(status_code=500, detail="Failed to search YouTube videos")

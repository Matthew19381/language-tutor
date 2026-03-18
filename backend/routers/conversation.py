import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.models.test_result import TestResult
from backend.models.lesson import Lesson
from backend.services.lesson_generator import (
    generate_conversation_scenario,
    analyze_conversation,
    analyze_pasted_conversation,
    answer_language_question
)
from backend.services.gemini_service import generate_text
from backend.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory conversation sessions (for simplicity)
# In production, use Redis or DB
conversation_sessions = {}


class StartConversationRequest(BaseModel):
    topic: Optional[str] = None


class MessageRequest(BaseModel):
    session_id: str
    user_message: str


class AnalyzeRequest(BaseModel):
    session_id: str
    user_id: Optional[int] = None


class QuestionRequest(BaseModel):
    question: str
    user_id: Optional[int] = None


class AnalyzePastedRequest(BaseModel):
    user_id: int
    pasted_text: str


@router.post("/api/conversation/start/{user_id}")
async def start_conversation(
    user_id: int,
    request: StartConversationRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get recent errors to incorporate
    recent_tests = db.query(TestResult).filter(
        TestResult.user_id == user_id
    ).order_by(TestResult.created_at.desc()).limit(3).all()

    user_errors = []
    for test in recent_tests:
        if test.errors:
            try:
                errors = json.loads(test.errors)
                user_errors.extend(errors[:2])
            except Exception:
                pass

    topic = request.topic or "everyday conversation"

    try:
        scenario = await generate_conversation_scenario(
            topic=topic,
            cefr_level=user.cefr_level,
            user_errors=user_errors,
            language=user.target_language,
            native_language=user.native_language
        )

        # Create session
        import uuid
        session_id = str(uuid.uuid4())
        conversation_sessions[session_id] = {
            "user_id": user_id,
            "scenario": scenario,
            "history": [],
            "language": user.target_language,
            "native_language": user.native_language,
            "cefr_level": user.cefr_level,
            "system_prompt": scenario.get("system_prompt", "")
        }

        # Add opening line to history
        opening_line = scenario.get("opening_line", "Hello! Let's start our conversation.")
        conversation_sessions[session_id]["history"].append({
            "role": "assistant",
            "content": opening_line
        })

        return {
            "success": True,
            "session_id": session_id,
            "scenario": scenario.get("scenario", ""),
            "ai_role": scenario.get("ai_role", ""),
            "user_role": scenario.get("user_role", ""),
            "suggested_phrases": scenario.get("suggested_phrases", []),
            "opening_line": opening_line
        }
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/conversation/message")
async def send_message(request: MessageRequest):
    session_id = request.session_id

    if session_id not in conversation_sessions:
        raise HTTPException(status_code=404, detail="Conversation session not found")

    session = conversation_sessions[session_id]
    language = session["language"]
    native_language = session["native_language"]
    cefr_level = session["cefr_level"]
    system_prompt = session["system_prompt"]

    # Add user message to history
    session["history"].append({
        "role": "user",
        "content": request.user_message
    })

    # Build prompt with history
    history_text = "\n".join([
        f"{'You' if msg['role'] == 'assistant' else 'Student'}: {msg['content']}"
        for msg in session["history"][-10:]  # Last 10 messages for context
    ])

    prompt = f"""{system_prompt}

Conversation so far:
{history_text}

Continue the conversation. Respond as the {session['scenario'].get('ai_role', 'conversation partner')}.
Keep the response appropriate for CEFR {cefr_level} level.
If the student makes a grammatical error, naturally incorporate the correct form in your response without explicitly correcting them harshly.
Response should be 1-3 sentences in {language}."""

    try:
        ai_response = await generate_text(prompt)
        ai_response = ai_response.strip()

        # Add AI response to history
        session["history"].append({
            "role": "assistant",
            "content": ai_response
        })

        return {
            "success": True,
            "response": ai_response,
            "message_count": len(session["history"])
        }
    except Exception as e:
        logger.error(f"Error generating conversation response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/conversation/analyze")
async def analyze_session(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    session_id = request.session_id

    if session_id not in conversation_sessions:
        raise HTTPException(status_code=404, detail="Conversation session not found")

    session = conversation_sessions[session_id]

    try:
        # Filter to only user messages for analysis
        user_messages = [
            msg for msg in session["history"]
            if msg["role"] == "user"
        ]

        if not user_messages:
            return {
                "success": True,
                "summary": "No messages to analyze yet.",
                "errors": [],
                "vocabulary_used": [],
                "recommendations": ["Start the conversation first!"],
                "score": 0
            }

        analysis = await analyze_conversation(
            conversation_history=session["history"],
            cefr_level=session["cefr_level"],
            language=session["language"],
            native_language=session["native_language"]
        )

        # Save errors to DB if user_id provided
        if request.user_id:
            user = db.query(User).filter(User.id == request.user_id).first()
            if user:
                errors = analysis.get("errors", [])
                test_result = TestResult(
                    user_id=request.user_id,
                    test_type="conversation",
                    score=analysis.get("score", 0),
                    answers=json.dumps({"messages": len(user_messages)}),
                    errors=json.dumps(errors),
                    cefr_level=session["cefr_level"],
                    language=session["language"]
                )
                db.add(test_result)

                # Award XP for conversation practice
                xp = min(30, int(analysis.get("score", 0) * 0.3))
                user.total_xp += xp
                db.commit()

                analysis["xp_earned"] = xp

        # Clear session after analysis
        del conversation_sessions[session_id]

        return {
            "success": True,
            **analysis
        }
    except Exception as e:
        logger.error(f"Error analyzing conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/conversation/question")
async def ask_question(
    request: QuestionRequest,
    db: Session = Depends(get_db)
):
    cefr_level = "B1"
    language = settings.TARGET_LANGUAGE
    native_language = settings.NATIVE_LANGUAGE

    if request.user_id:
        user = db.query(User).filter(User.id == request.user_id).first()
        if user:
            cefr_level = user.cefr_level
            language = user.target_language
            native_language = user.native_language

    try:
        answer = await answer_language_question(
            question=request.question,
            cefr_level=cefr_level,
            language=language,
            native_language=native_language
        )
        return {
            "success": True,
            "question": request.question,
            "answer": answer
        }
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/conversation/grok-prompt")
async def get_grok_prompt(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get latest lesson topic
    latest_lesson = db.query(Lesson).filter(
        Lesson.user_id == user_id
    ).order_by(Lesson.created_at.desc()).first()

    topic = latest_lesson.topic if latest_lesson else "everyday conversation"
    lesson_title = latest_lesson.title if latest_lesson else "General"

    # Get recent errors
    recent_tests = db.query(TestResult).filter(
        TestResult.user_id == user_id
    ).order_by(TestResult.created_at.desc()).limit(3).all()

    weak_areas_seen = set()
    weak_areas = []
    for test in recent_tests:
        if test.errors:
            try:
                import json as json_module
                errors = json_module.loads(test.errors)
                for err in errors[:2]:
                    if isinstance(err, dict):
                        err_type = err.get("type", err.get("error", ""))
                        if err_type and err_type not in weak_areas_seen:
                            weak_areas.append(str(err_type)[:60])
                            weak_areas_seen.add(err_type)
            except Exception:
                pass

    weak_areas_text = ", ".join(weak_areas[:4]) if weak_areas else "general grammar"

    prompt = f"""Jesteś nauczycielem języka {user.target_language}. Mój język ojczysty to polski.
Mój aktualny poziom: {user.cefr_level}
Dzisiaj uczyłem/am się: {topic} ({lesson_title})
Moje słabe obszary: {weak_areas_text}

Proszę, rozmawiaj ze mną po {user.target_language} na poziomie {user.cefr_level}. Poprawiaj moje błędy delikatnie (pokazuj poprawną formę w nawiasach kwadratowych). Pomóż mi ćwiczyć: {topic}. Zacznij od krótkiego wprowadzenia do dzisiejszego tematu, a następnie zaangażuj mnie w rozmowę."""

    return {
        "success": True,
        "prompt": prompt,
        "level": user.cefr_level,
        "language": user.target_language,
        "topic": topic,
        "weak_areas": weak_areas[:4]
    }


@router.post("/api/conversation/analyze-text")
async def analyze_pasted_text(
    request: AnalyzePastedRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not request.pasted_text.strip():
        raise HTTPException(status_code=400, detail="No text provided")

    try:
        analysis = await analyze_pasted_conversation(
            pasted_text=request.pasted_text,
            cefr_level=user.cefr_level,
            language=user.target_language,
            native_language=user.native_language
        )

        # Save to TestResult
        errors = analysis.get("errors", [])
        test_result = TestResult(
            user_id=request.user_id,
            test_type="conversation_paste",
            score=analysis.get("score", 0),
            answers=json.dumps({"source": "pasted_text", "length": len(request.pasted_text)}),
            errors=json.dumps(errors),
            cefr_level=user.cefr_level,
            language=user.target_language
        )
        db.add(test_result)

        xp = min(20, int(analysis.get("score", 0) * 0.2))
        user.total_xp += xp
        db.commit()

        analysis["xp_earned"] = xp
        return {"success": True, **analysis}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing pasted text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

"""Pydantic schemas for conversation router."""
from pydantic import BaseModel
from typing import Optional, List


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


class TranslateRequest(BaseModel):
    text: str
    from_lang: str
    to_lang: str

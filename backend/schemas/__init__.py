"""
Pydantic schemas for LinguaAI.
Unified standard across all ecosystem modules.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# User schemas
class UserCreate(BaseModel):
    name: str
    target_language: str
    native_language: str = "pl"


class UserResponse(BaseModel):
    id: int
    name: str
    target_language: str
    native_language: str
    level: int
    xp: int
    streak_days: int
    created_at: datetime

    class Config:
        orm_mode = True


# Lesson schemas
class LessonCreate(BaseModel):
    user_id: int
    topic: str
    day_offset: int = 0


class LessonResponse(BaseModel):
    id: int
    user_id: int
    topic: str
    content: Dict[str, Any]
    day_number: int
    is_completed: bool
    created_at: datetime

    class Config:
        orm_mode = True


# Test schemas
class TestSubmit(BaseModel):
    user_id: int
    lesson_id: Optional[int] = None
    answers: List[Dict[str, Any]]
    time_taken: int  # seconds


class TestResultResponse(BaseModel):
    id: int
    user_id: int
    score: float
    total_questions: int
    correct_answers: int
    xp_earned: int
    created_at: datetime

    class Config:
        orm_mode = True


# Flashcard schemas
class FlashcardCreate(BaseModel):
    user_id: int
    front: str
    back: str
    lesson_id: Optional[int] = None
    lesson_day: Optional[int] = None


class FlashcardReview(BaseModel):
    rating: str  # Again / Hard / Good / Easy


class FlashcardResponse(BaseModel):
    id: int
    user_id: int
    front: str
    back: str
    ease_factor: float
    interval_days: int
    next_review_date: datetime
    lesson_id: Optional[int] = None

    class Config:
        orm_mode = True


# Conversation schemas
class ConversationStart(BaseModel):
    user_id: int
    topic: Optional[str] = None


class MessageSend(BaseModel):
    session_id: int
    user_message: str


# Stats schemas
class AddXP(BaseModel):
    amount: int
    reason: str


class StatsResponse(BaseModel):
    user_id: int
    xp: int
    level: int
    xp_for_next_level: int
    streak_days: int
    today_lessons: int
    today_tests: int
    today_conversations: int
    new_achievements: List[Dict[str, Any]] = []

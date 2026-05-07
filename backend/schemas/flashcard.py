"""Pydantic schemas for flashcard router."""
from pydantic import BaseModel
from typing import Optional


class ReviewFlashcardRequest(BaseModel):
    rating: int  # 1-4 button rating


class AddFlashcardRequest(BaseModel):
    front: str
    back: str
    language: Optional[str] = None


class AddFlashcardAIRequest(BaseModel):
    word: str
    language: Optional[str] = None

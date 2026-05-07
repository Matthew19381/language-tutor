"""Pydantic schemas for flashcard router."""
from pydantic import BaseModel
from typing import Optional


class ReviewFlashcardRequest(BaseModel):
    rating: int  # 1-4 button rating


class AddFlashcardRequest(BaseModel):
    word: str
    translation: str
    example_sentence: Optional[str] = None


class AddFlashcardAIRequest(BaseModel):
    word: str


class ConceptFlashcardRequest(BaseModel):
    lesson_id: int
    concepts: list

"""Pydantic schemas for pronunciation router."""
from pydantic import BaseModel
from typing import Optional


class AnalyzePronunciationRequest(BaseModel):
    user_id: int
    target_text: str
    audio_filename: Optional[str] = None

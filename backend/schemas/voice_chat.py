"""Pydantic schemas for voice chat router."""
from pydantic import BaseModel
from typing import Optional


class VoiceChatMessageRequest(BaseModel):
    user_id: int
    message: str
    language: str = "German"


class VoiceChatPromptResponse(BaseModel):
    prompt: str
    language: str
    has_lesson_today: bool
    due_flashcards: int
    error_count: int


class VoiceChatTextResponse(BaseModel):
    success: bool
    text: str


class VoiceChatVoiceResponse(BaseModel):
    success: bool
    text: str
    audio_base64: str
    message: str = ""

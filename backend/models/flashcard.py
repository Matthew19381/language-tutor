from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, date
from backend.database import Base


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word = Column(String, nullable=False)
    translation = Column(String, nullable=False)
    example_sentence = Column(Text, nullable=True)
    audio_path = Column(String, nullable=True)
    language = Column(String, nullable=False)
    cefr_level = Column(String, nullable=False)
    lesson_id = Column(Integer, nullable=True)
    lesson_day = Column(Integer, nullable=True)
    lesson_topic = Column(String, nullable=True)
    ease_factor = Column(Float, default=2.5)
    interval_days = Column(Integer, default=1)
    next_review_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="flashcards")

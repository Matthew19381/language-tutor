from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    native_language = Column(String, default="Polish")
    target_language = Column(String, default="German")
    cefr_level = Column(String, default="A1")
    streak_days = Column(Integer, default=0)
    streak_freezes = Column(Integer, default=2)  # 2 freezes granted by default
    total_xp = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    # JSON: {"German": "B1", "Spanish": "A2", ...} — CEFR per language
    language_profiles = Column(Text, default="{}")

    lessons = relationship("Lesson", back_populates="user")
    test_results = relationship("TestResult", back_populates="user")
    flashcards = relationship("Flashcard", back_populates="user")
    study_plans = relationship("StudyPlan", back_populates="user")
    achievements = relationship("Achievement", back_populates="user")
    topics = relationship("Topic", back_populates="user")

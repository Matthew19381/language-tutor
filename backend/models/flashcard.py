from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, date, timezone
from backend.database import Base


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    word = Column(String, nullable=False)
    translation = Column(String, nullable=False)
    example_sentence = Column(Text, nullable=True)
    audio_path = Column(String, nullable=True)
    language = Column(String, nullable=False)
    cefr_level = Column(String, nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=True)
    lesson_day = Column(Integer, nullable=True)
    lesson_topic = Column(String, nullable=True)
    gender = Column(String, nullable=True)  # der/die/das for German nouns
    # ── FSRS Spaced Repetition ──
    difficulty = Column(Float, default=5.0)          # FSRS difficulty (0-10, lower=easier)
    stability = Column(Float, default=0.0)           # FSRS stability (days)
    retrievability = Column(Float, default=0.0)      # FSRS retrievability (0-1)
    interval_days = Column(Integer, default=1)       # days until next review
    repetitions = Column(Integer, default=0)         # total review count
    lapses = Column(Integer, default=0)              # times forgotten
    fsrs_state = Column(String, default="Learning")  # Learning/Review/Relearning
    next_review_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="flashcards")

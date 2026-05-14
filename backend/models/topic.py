"""
Topic & TopicItem models — thematic organization of lessons/tests/exercises
with SM-2 spaced repetition per topic.

Topic = a grammar/vocabulary theme (e.g. "Perfekt", "Konjunktiv II")
TopicItem = a lesson, test, or exercise linked to a topic
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum
from backend.database import Base


class TopicCategory(str, enum.Enum):
    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"
    PRONUNCIATION = "pronunciation"
    LISTENING = "listening"
    READING = "reading"
    WRITING = "writing"
    SPEAKING = "speaking"
    CULTURE = "culture"
    IDIOMS = "idioms"
    OTHER = "other"


class ItemType(str, enum.Enum):
    LESSON = "lesson"
    EXERCISE = "exercise"
    TEST = "test"
    CONVERSATION = "conversation"
    NEWS = "news"
    PRONUNCIATION = "pronunciation"


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    language = Column(String, nullable=False)          # e.g. "German"
    category = Column(String, default=TopicCategory.GRAMMAR)
    name = Column(String, nullable=False)              # e.g. "Perfekt"
    description = Column(Text, nullable=True)           # AI-generated summary
    cefr_level = Column(String, nullable=True)          # A1-C2

    # ── SM-2 Spaced Repetition ──
    easiness_factor = Column(Float, default=2.5)        # EF, starts at 2.5
    interval = Column(Integer, default=0)               # days until next review
    repetitions = Column(Integer, default=0)            # consecutive successful reviews
    next_review_date = Column(DateTime, nullable=True)  # when to review next
    last_review_date = Column(DateTime, nullable=True)  # last time reviewed
    memory_strength = Column(Float, default=0.0)        # 0.0-1.0 visual indicator

    # ── Stats ──
    total_items = Column(Integer, default=0)            # total lessons+tests+exercises
    total_reviews = Column(Integer, default=0)          # total times reviewed
    avg_score = Column(Float, default=0.0)              # average score across reviews

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Relationships ──
    user = relationship("User", back_populates="topics")
    items = relationship("TopicItem", back_populates="topic", cascade="all, delete-orphan")

    def calculate_memory_strength(self) -> float:
        """
        Calculate memory strength 0.0-1.0 based on SM-2 state.
        Considers: repetitions, interval, easiness_factor, time since last review.
        """
        if self.repetitions == 0:
            return 0.0

        # Base strength from repetitions (diminishing returns)
        rep_strength = min(1.0, self.repetitions / 5.0)

        # Interval factor: longer interval = stronger memory
        interval_strength = min(1.0, self.interval / 30.0)

        # EF factor: higher EF = easier to remember
        ef_strength = min(1.0, (self.easiness_factor - 1.3) / 1.2)

        # Decay: reduce strength based on time elapsed since last review
        if self.last_review_date and self.interval > 0:
            days_since = (datetime.utcnow() - self.last_review_date).days
            decay = max(0.0, 1.0 - (days_since / max(self.interval * 1.5, 1)))
        else:
            decay = 0.5  # neutral if no review yet

        # Weighted combination
        strength = (
            rep_strength * 0.25 +
            interval_strength * 0.25 +
            ef_strength * 0.20 +
            decay * 0.30
        )
        return round(min(1.0, max(0.0, strength)), 2)

    def is_due(self) -> bool:
        """Check if topic is due for review."""
        if self.next_review_date is None:
            return True  # never reviewed = due
        return datetime.utcnow() >= self.next_review_date

    def days_until_review(self) -> int:
        """Days until next review (negative = overdue)."""
        if self.next_review_date is None:
            return 0
        delta = (self.next_review_date - datetime.utcnow()).days
        return delta

    def apply_sm2(self, quality: int) -> None:
        """
        Apply SM-2 algorithm after a review.

        Args:
            quality: 0-5 rating
              0 = complete blackout
              1 = incorrect, remembered on seeing answer
              2 = incorrect, but easy to recall answer
              3 = correct with serious difficulty
              4 = correct with some hesitation
              5 = perfect response
        """
        quality = max(0, min(5, quality))

        old_ef = self.easiness_factor
        new_ef = old_ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        self.easiness_factor = max(1.3, new_ef)

        if quality < 3:
            # Failed review — reset repetitions but keep interval at minimum
            self.repetitions = 0
            self.interval = 1
        else:
            self.repetitions += 1
            if self.repetitions == 1:
                self.interval = 1
            elif self.repetitions == 2:
                self.interval = 6
            else:
                self.interval = int(self.interval * self.easiness_factor)

        self.last_review_date = datetime.utcnow()
        self.next_review_date = datetime.utcnow() + timedelta(days=self.interval)
        self.memory_strength = self.calculate_memory_strength()
        self.total_reviews += 1
        self.updated_at = datetime.utcnow()


class TopicItem(Base):
    __tablename__ = "topic_items"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False, index=True)
    item_type = Column(String, nullable=False)          # lesson, exercise, test, etc.
    item_id = Column(Integer, nullable=False)           # FK to lesson/test/etc. table
    title = Column(String, nullable=True)               # snapshot title
    day_number = Column(Integer, nullable=True)         # lesson day if applicable
    score = Column(Float, nullable=True)                # test/exercise score if applicable
    created_at = Column(DateTime, default=datetime.utcnow)

    topic = relationship("Topic", back_populates="items")

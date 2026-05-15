from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class TestResult(Base):
    __tablename__ = "test_results"
    __table_args__ = (
        UniqueConstraint('user_id', 'test_type', 'language', 'created_at', name='uq_user_test_type_lang_date'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    test_type = Column(String, nullable=False)  # daily / weekly / placement
    score = Column(Float, nullable=False)  # 0-100
    answers = Column(Text, nullable=False)  # JSON text
    errors = Column(Text, nullable=True)  # JSON text - list of error objects
    cefr_level = Column(String, nullable=False)
    language = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="test_results")

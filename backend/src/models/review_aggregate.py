"""Review aggregate model for summarized wine reviews."""

from sqlalchemy import Column, ForeignKey, Integer, Numeric, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class ReviewAggregate(Base):
    """Aggregated review data for a wine."""

    __tablename__ = "review_aggregates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    wine_id = Column(Integer, ForeignKey("wines.id", ondelete="CASCADE"), nullable=False, unique=True)
    avg_rating = Column(Numeric(3, 1), nullable=True)
    rating_scale = Column(Numeric(3, 1), nullable=True)  # e.g., 5.0 for 5-star scale
    descriptors = Column(JSONB, nullable=True)  # {"tags": [...], "confidence": 0.8}
    pros = Column(JSONB, nullable=True)
    cons = Column(JSONB, nullable=True)
    disagreement_summary = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    wine = relationship("Wine", back_populates="review_aggregate")

"""External reviews and aggregates."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Text
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base


class ExternalReview(Base):
    __tablename__ = "external_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    wine_id = Column(Integer, ForeignKey("wines.id"), nullable=False)
    source_name = Column(String(200), nullable=True)
    source_url = Column(String(1000), nullable=True)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    raw_ref = Column(String(500), nullable=True)
    extracted_json = Column(JSONB, nullable=True)


class ReviewAggregate(Base):
    __tablename__ = "review_aggregates"

    wine_id = Column(Integer, ForeignKey("wines.id"), primary_key=True)
    avg_rating = Column(String(50), nullable=True)  # nullable for scale flexibility
    rating_scale = Column(String(50), nullable=True)
    descriptors = Column(JSONB, nullable=True)  # tags + confidence
    pros = Column(JSONB, nullable=True)
    cons = Column(JSONB, nullable=True)
    disagreement_summary = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

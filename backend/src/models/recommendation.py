"""Recommendation run and output models."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, func, Text
from .base import Base


class RecommendationRun(Base):
    __tablename__ = "recommendation_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mode = Column(String(20), nullable=False)  # daily, weekly, manual
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="running")  # success, fail, running
    logs_ref = Column(String(500), nullable=True)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(Integer, ForeignKey("recommendation_runs.id"), nullable=False)
    user_id = Column(String(1), ForeignKey("users.id"), nullable=False)
    kind = Column(String(30), nullable=False)  # recommended_buys, cheapest_favorites
    rank = Column(Integer, nullable=False)
    wine_id = Column(Integer, ForeignKey("wines.id"), nullable=False)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=True)
    score = Column(Numeric(5, 2), nullable=True)
    explanation = Column(Text, nullable=True)
    explanation_locale = Column(String(5), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

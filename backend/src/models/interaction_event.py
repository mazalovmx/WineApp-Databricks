"""Interaction events for analytics (optional MVP+)."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base


class InteractionEvent(Base):
    __tablename__ = "interaction_events"

    event_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(1), ForeignKey("users.id"), nullable=True)
    event_type = Column(String(50), nullable=False)  # view, click, filter_change
    payload = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

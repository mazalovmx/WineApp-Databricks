"""User model - exactly two users (A and B)."""
from sqlalchemy import Column, Integer, String, DateTime, func
from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(String(1), primary_key=True)  # 'A' or 'B'
    display_name = Column(String(100), nullable=False)
    locale = Column(String(5), default="en")  # en, ru
    created_at = Column(DateTime(timezone=True), server_default=func.now())

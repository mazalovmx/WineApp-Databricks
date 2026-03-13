"""User rating model - tasting feedback."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Text
from .base import Base


class UserRating(Base):
    __tablename__ = "user_ratings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(1), ForeignKey("users.id"), nullable=False)
    wine_id = Column(Integer, ForeignKey("wines.id"), nullable=False)
    rating_1_5 = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    tried_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

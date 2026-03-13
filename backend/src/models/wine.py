"""Wine canonical entity model."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from .base import Base, TimestampMixin


class Wine(Base, TimestampMixin):
    __tablename__ = "wines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    canonical_name = Column(String(300), nullable=False)
    producer = Column(String(200), nullable=True)
    country = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    type_ = Column("type", String(50), nullable=True)  # red, white, rose, sparkling, other
    grapes = Column(ARRAY(String), nullable=True)
    sweetness = Column(String(20), default="unknown")  # dry, off-dry, sweet
    is_grape_wine = Column(Boolean, default=True)

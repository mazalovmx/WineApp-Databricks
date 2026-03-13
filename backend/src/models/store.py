"""Store model - supermarkets and specialty wine shops."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from .base import Base, TimestampMixin


class Store(Base, TimestampMixin):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)  # supermarket, specialty
    base_url = Column(String(500), nullable=True)
    enabled = Column(Boolean, default=True)

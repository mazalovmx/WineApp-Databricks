"""Price history model for tracking wine prices over time."""

from sqlalchemy import Column, ForeignKey, Integer, Numeric, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class PriceHistory(Base):
    """Historical price records for wine at a store."""

    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    wine_id = Column(Integer, ForeignKey("wines.id", ondelete="CASCADE"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False)
    price_mxn = Column(Numeric(10, 2), nullable=False)
    captured_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    wine = relationship("Wine", back_populates="price_history")
    store = relationship("Store", back_populates="price_history")

"""Offer and price history models."""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from .base import Base, TimestampMixin


class Offer(Base, TimestampMixin):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    wine_id = Column(Integer, ForeignKey("wines.id"), nullable=True)
    listed_name = Column(String(500), nullable=False)
    price_mxn = Column(Numeric(10, 2), nullable=False)
    discount_text = Column(String(100), nullable=True)
    volume_ml = Column(Integer, nullable=True)
    availability = Column(String(20), default="unknown")  # in_stock, unknown, out_of_stock
    product_url = Column(String(1000), nullable=True)
    captured_at = Column(DateTime(timezone=True), nullable=False)


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    wine_id = Column(Integer, ForeignKey("wines.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    price_mxn = Column(Numeric(10, 2), nullable=False)
    captured_at = Column(DateTime(timezone=True), server_default=func.now())

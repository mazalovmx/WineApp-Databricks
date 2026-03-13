"""Raw page snapshot model for audit/debugging."""
from sqlalchemy import Column, Integer, String, DateTime, func
from .base import Base


class RawPage(Base):
    __tablename__ = "raw_pages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, nullable=True)
    url = Column(String(1000), nullable=False)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    content_ref = Column(String(500), nullable=True)  # object storage path
    content_hash = Column(String(64), nullable=True)
    fetch_status = Column(String(20), default="success")  # success, fail

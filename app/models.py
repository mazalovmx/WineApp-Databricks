from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(1), primary_key=True)  # A/B
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    locale: Mapped[str] = mapped_column(String(8), default="en", nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(32), nullable=False)  # supermarket/specialty
    base_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Wine(Base):
    __tablename__ = "wines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    producer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    grapes: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    sweetness: Mapped[str] = mapped_column(String(32), default="unknown", nullable=False)
    is_grape_wine: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class Offer(Base):
    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    wine_id: Mapped[int | None] = mapped_column(ForeignKey("wines.id"), nullable=True)
    listed_name: Mapped[str] = mapped_column(String(255), nullable=False)
    price_mxn: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    volume_ml: Mapped[int | None] = mapped_column(Integer, nullable=True)
    availability: Mapped[str] = mapped_column(String(32), default="unknown", nullable=False)
    product_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    match_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    wine_id: Mapped[int] = mapped_column(ForeignKey("wines.id"), nullable=False)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    price_mxn: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class RawPage(Base):
    __tablename__ = "raw_pages"
    __table_args__ = (UniqueConstraint("url", "content_hash", name="uq_raw_pages_url_hash"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    content_ref: Mapped[str] = mapped_column(String(2048), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    fetch_status: Mapped[str] = mapped_column(String(64), nullable=False, default="success")


class ExternalReview(Base):
    __tablename__ = "external_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    wine_id: Mapped[int] = mapped_column(ForeignKey("wines.id"), nullable=False)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    raw_ref: Mapped[str] = mapped_column(String(2048), nullable=False)
    extracted_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)


class ReviewAggregate(Base):
    __tablename__ = "review_aggregates"

    wine_id: Mapped[int] = mapped_column(ForeignKey("wines.id"), primary_key=True)
    avg_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    rating_scale: Mapped[str | None] = mapped_column(String(16), nullable=True)
    descriptors: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    pros: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    cons: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    disagreement_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class UserRating(Base):
    __tablename__ = "user_ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    wine_id: Mapped[int] = mapped_column(ForeignKey("wines.id"), nullable=False)
    rating_1_5: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    tried_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class RecommendationRun(Base):
    __tablename__ = "recommendation_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # run_id
    mode: Mapped[str] = mapped_column(String(16), nullable=False)  # daily/weekly/manual
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False)  # success/fail
    logs_ref: Mapped[str] = mapped_column(String(2048), nullable=False)


class Recommendation(Base):
    __tablename__ = "recommendations"
    __table_args__ = (UniqueConstraint("run_id", "user_id", "kind", "rank", name="uq_reco_rank"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("recommendation_runs.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    wine_id: Mapped[int] = mapped_column(ForeignKey("wines.id"), nullable=False)
    offer_id: Mapped[int | None] = mapped_column(ForeignKey("offers.id"), nullable=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    explanation_locale: Mapped[str] = mapped_column(String(8), nullable=False, default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class InteractionEvent(Base):
    __tablename__ = "interaction_events"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

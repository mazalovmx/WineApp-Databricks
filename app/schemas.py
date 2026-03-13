from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    user_id: str = Field(pattern="^(A|B)$")
    password: str = Field(min_length=3)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserMeResponse(BaseModel):
    id: str
    display_name: str
    locale: str


class HealthResponse(BaseModel):
    status: str
    last_successful_run: datetime | None
    data_freshness: str


class RecommendationItem(BaseModel):
    rank: int
    wine_id: int
    offer_id: int | None
    score: float
    explanation: str
    explanation_locale: str


class RecommendationsResponse(BaseModel):
    run_id: str
    kind: str
    items: list[RecommendationItem]


class TriedWineItem(BaseModel):
    wine_id: int
    canonical_name: str
    ratings: list[dict[str, Any]]
    last_known_offer_price: float | None


class RatingCreateRequest(BaseModel):
    wine_id: int
    rating_1_5: int = Field(ge=1, le=5)
    comment: str | None = None
    tried_at: datetime | None = None


class TriggerRunRequest(BaseModel):
    mode: str = Field(pattern="^(daily|weekly|manual)$")

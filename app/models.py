from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class WineDeal(BaseModel):
    id: Optional[int] = None
    name: str
    region: str = ""
    grape: str = ""
    original_price: float
    deal_price: float
    discount_pct: float = Field(default=0.0)
    source: str = ""
    url: str = ""
    image_url: str = ""
    deal_date: date = Field(default_factory=date.today)
    created_at: Optional[datetime] = None

    def model_post_init(self, __context: object) -> None:
        if self.original_price > 0 and self.discount_pct == 0.0:
            self.discount_pct = round(
                (1 - self.deal_price / self.original_price) * 100, 1
            )


class DealSummary(BaseModel):
    total_deals: int = 0
    avg_discount: float = 0.0
    best_deal: Optional[WineDeal] = None
    deal_date: date = Field(default_factory=date.today)

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from app.matching import match_listed_wine


@dataclass(slots=True)
class SearchResult:
    title: str
    url: str
    snippet: str


class LLMClient(Protocol):
    def search(self, query: str) -> list[SearchResult]:
        ...

    def extract_offers(self, page_text: str, schema: dict) -> dict:
        ...

    def summarize_reviews(self, texts: list[str]) -> dict:
        ...

    def match_wine_entity(self, listed_name: str, candidates: list[tuple[int, str]]) -> dict:
        ...


class MockLLMClient:
    """
    Deterministic local adapter used for MVP/testing.
    Replacing this class with a real provider should not require business-logic rewrites.
    """

    def search(self, query: str) -> list[SearchResult]:
        return [
            SearchResult(
                title=f"Search result for {query}",
                url="https://example.com/review",
                snippet="Balanced acidity, good value, mixed opinions on finish.",
            )
        ]

    def extract_offers(self, page_text: str, schema: dict) -> dict:
        offers: list[dict[str, object]] = []
        # Expected line format:
        # Name | 199 | discount:-20% | 750 | in_stock | https://...
        for raw_line in page_text.splitlines():
            line = raw_line.strip()
            if not line or "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 6:
                continue
            name, price, discount, volume, availability, url = parts[:6]
            if not re.match(r"^\d+(\.\d+)?$", price):
                continue
            offers.append(
                {
                    "product_name": name,
                    "price_mxn": float(price),
                    "discount_text": None if discount.lower() in {"none", "null", ""} else discount,
                    "volume_ml": int(volume) if volume.isdigit() else None,
                    "availability": availability,
                    "url": url,
                    "confidence": 0.9,
                }
            )
        return {"offers": offers}

    def summarize_reviews(self, texts: list[str]) -> dict:
        descriptor = "fruity"
        if any("oak" in t.lower() for t in texts):
            descriptor = "oaky"
        return {
            "avg_rating": 4.0,
            "rating_scale": "5",
            "descriptors": [{"tag": descriptor, "confidence": 0.8}],
            "pros": ["good value", "balanced taste"],
            "cons": ["finish may vary"],
            "disagreement_summary": "Reviewers disagree on finish smoothness.",
        }

    def match_wine_entity(self, listed_name: str, candidates: list[tuple[int, str]]) -> dict:
        result = match_listed_wine(listed_name, candidates)
        return {"wine_id": result.wine_id, "confidence": result.confidence, "reason": result.reason}

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Protocol

import httpx

from app.config import settings
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


class HTTPToolLLMClient:
    """
    Generic HTTP adapter for provider-agnostic integration.
    Any external LLM gateway can be used if it supports the JSON contract below.
    """

    def __init__(
        self,
        *,
        search_url: str,
        extract_offers_url: str,
        summarize_reviews_url: str,
        match_entity_url: str,
        headers: dict[str, str] | None = None,
        timeout_seconds: float = 30,
        client: httpx.Client | None = None,
    ) -> None:
        self.search_url = search_url
        self.extract_offers_url = extract_offers_url
        self.summarize_reviews_url = summarize_reviews_url
        self.match_entity_url = match_entity_url
        self.headers = headers or {}
        self.timeout_seconds = timeout_seconds
        self._client = client or httpx.Client(timeout=self.timeout_seconds)

    def _post(self, url: str, payload: dict[str, object]) -> dict:
        response = self._client.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON object from {url}.")
        return data

    def search(self, query: str) -> list[SearchResult]:
        data = self._post(self.search_url, {"query": query})
        rows = data.get("results", [])
        if not isinstance(rows, list):
            return []
        results: list[SearchResult] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            results.append(
                SearchResult(
                    title=str(row.get("title", "")),
                    url=str(row.get("url", "")),
                    snippet=str(row.get("snippet", "")),
                )
            )
        return results

    def extract_offers(self, page_text: str, schema: dict) -> dict:
        return self._post(self.extract_offers_url, {"page_text": page_text, "schema": schema})

    def summarize_reviews(self, texts: list[str]) -> dict:
        return self._post(self.summarize_reviews_url, {"texts": texts})

    def match_wine_entity(self, listed_name: str, candidates: list[tuple[int, str]]) -> dict:
        serialized = [{"wine_id": wine_id, "canonical_name": canonical_name} for wine_id, canonical_name in candidates]
        return self._post(
            self.match_entity_url,
            {"listed_name": listed_name, "candidates": serialized},
        )


def build_llm_client_from_settings() -> LLMClient:
    provider = settings.llm_provider.strip().lower()
    if provider == "mock":
        return MockLLMClient()
    if provider == "generic_http":
        headers = json.loads(settings.llm_headers_json) if settings.llm_headers_json else {}
        if not all(
            [
                settings.llm_search_url,
                settings.llm_extract_offers_url,
                settings.llm_summarize_reviews_url,
                settings.llm_match_entity_url,
            ]
        ):
            raise ValueError("generic_http provider requires all LLM_*_URL settings.")
        return HTTPToolLLMClient(
            search_url=settings.llm_search_url,
            extract_offers_url=settings.llm_extract_offers_url,
            summarize_reviews_url=settings.llm_summarize_reviews_url,
            match_entity_url=settings.llm_match_entity_url,
            headers={str(k): str(v) for k, v in headers.items()},
            timeout_seconds=settings.llm_timeout_seconds,
        )
    raise ValueError(f"Unsupported LLM_PROVIDER '{settings.llm_provider}'.")

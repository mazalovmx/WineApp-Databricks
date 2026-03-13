"""Mock LLM adapter for tests and development without API keys."""
import json
from .base import LLMClientBase, SearchResult, SearchResults


class MockLLMAdapter(LLMClientBase):
    """Mock implementation for testing - returns deterministic fixtures."""

    async def search(self, query: str, max_results: int = 10) -> SearchResults:
        return SearchResults(
            results=[
                SearchResult(
                    title="Sample store - Wine catalog",
                    url="https://example.com/wines",
                    snippet="Red and white wines from Mexico and abroad.",
                )
            ],
            query=query,
            total=1,
        )

    async def extract_offers(self, page_text: str, schema: dict, **kwargs) -> dict:
        # Return minimal valid structure (use listed_name per schema)
        return {
            "offers": [
                {
                    "listed_name": "Vino Tinto Ejemplo 750ml",
                    "price_mxn": 199.0,
                    "discount_text": None,
                    "volume_ml": 750,
                    "availability": "in_stock",
                    "product_url": "https://example.com/product/1",
                    "confidence": 0.9,
                }
            ],
            "confidence": 0.85,
        }

    async def summarize_reviews(self, texts: list[str]) -> dict:
        return {
            "avg_rating": 4.0,
            "rating_scale": 5,
            "descriptors": [{"tag": "fruity", "confidence": 0.8}],
            "pros": ["Good value", "Easy drinking"],
            "cons": [],
            "disagreement_summary": "unknown",
            "confidence": 0.7,
        }

    async def match_wine_entity(self, listed_name: str, candidates: list[dict]) -> dict:
        return {
            "matched_id": candidates[0]["id"] if candidates else None,
            "confidence": 0.6,
            "canonical_name": listed_name[:100],
        }

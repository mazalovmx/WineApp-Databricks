from __future__ import annotations

import httpx
import pytest

from app.config import settings
from app.llm_client import HTTPToolLLMClient, MockLLMClient, build_llm_client_from_settings


def test_search_returns_expected_stub_shape() -> None:
    client = MockLLMClient()
    rows = client.search("cheap cabernet guadalajara")
    assert len(rows) == 1
    assert "cheap cabernet guadalajara" in rows[0].title
    assert rows[0].url.startswith("https://")


def test_extract_offers_parses_valid_rows_and_skips_invalid() -> None:
    client = MockLLMClient()
    raw = "\n".join(
        [
            "Wine A | 199 | discount:-10% | 750 | in_stock | https://example.com/a",
            "Malformed row without separators",
            "Wine B | not-a-price | none | 750 | in_stock | https://example.com/b",
            "Wine C | 229 | none | x750 | unknown | https://example.com/c",
        ]
    )
    payload = client.extract_offers(raw, schema={})
    assert len(payload["offers"]) == 2
    first = payload["offers"][0]
    second = payload["offers"][1]
    assert first["product_name"] == "Wine A"
    assert first["discount_text"] == "discount:-10%"
    assert second["product_name"] == "Wine C"
    assert second["volume_ml"] is None
    assert second["discount_text"] is None


def test_summarize_reviews_detects_oaky_descriptor() -> None:
    client = MockLLMClient()
    summary = client.summarize_reviews(["Strong oak aroma and vanilla notes."])
    assert summary["descriptors"][0]["tag"] == "oaky"


def test_match_wine_entity_returns_null_for_low_confidence() -> None:
    client = MockLLMClient()
    matched = client.match_wine_entity(
        "Whisky Honey Blend",
        [(1, "Trapiche Malbec Reserve"), (2, "Casillero Cabernet")],
    )
    assert matched["wine_id"] is None
    assert matched["confidence"] < 0.6


def test_generic_http_adapter_parses_all_tool_calls() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/search":
            return httpx.Response(200, json={"results": [{"title": "t", "url": "https://u", "snippet": "s"}]})
        if request.url.path == "/extract":
            return httpx.Response(200, json={"offers": []})
        if request.url.path == "/summarize":
            return httpx.Response(
                200,
                json={
                    "avg_rating": 4.0,
                    "rating_scale": "5",
                    "descriptors": [{"tag": "fruity", "confidence": 0.8}],
                    "pros": [],
                    "cons": [],
                    "disagreement_summary": "none",
                },
            )
        if request.url.path == "/match":
            return httpx.Response(200, json={"wine_id": 1, "confidence": 0.91, "reason": "match"})
        return httpx.Response(404, json={"detail": "unknown path"})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport, base_url="https://llm.local") as client:
        adapter = HTTPToolLLMClient(
            search_url="https://llm.local/search",
            extract_offers_url="https://llm.local/extract",
            summarize_reviews_url="https://llm.local/summarize",
            match_entity_url="https://llm.local/match",
            headers={"x-api-key": "demo"},
            client=client,
        )
        rows = adapter.search("query")
        assert len(rows) == 1
        assert rows[0].url == "https://u"
        assert adapter.extract_offers("raw", {}) == {"offers": []}
        summary = adapter.summarize_reviews(["a", "b"])
        assert summary["avg_rating"] == 4.0
        matched = adapter.match_wine_entity("name", [(1, "wine")])
        assert matched["wine_id"] == 1


def test_llm_factory_returns_mock_and_validates_generic_http() -> None:
    original = {
        "llm_provider": settings.llm_provider,
        "llm_search_url": settings.llm_search_url,
        "llm_extract_offers_url": settings.llm_extract_offers_url,
        "llm_summarize_reviews_url": settings.llm_summarize_reviews_url,
        "llm_match_entity_url": settings.llm_match_entity_url,
        "llm_headers_json": settings.llm_headers_json,
    }
    try:
        settings.llm_provider = "mock"
        assert isinstance(build_llm_client_from_settings(), MockLLMClient)

        settings.llm_provider = "generic_http"
        settings.llm_search_url = ""
        settings.llm_extract_offers_url = ""
        settings.llm_summarize_reviews_url = ""
        settings.llm_match_entity_url = ""
        with pytest.raises(ValueError):
            build_llm_client_from_settings()
    finally:
        for key, value in original.items():
            setattr(settings, key, value)

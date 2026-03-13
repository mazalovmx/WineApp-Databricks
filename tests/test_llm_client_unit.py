from __future__ import annotations

from app.llm_client import MockLLMClient


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

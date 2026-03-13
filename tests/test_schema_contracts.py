import pytest

from app.schema_validation import load_schema, validate_json


def test_offers_schema_accepts_valid_payload() -> None:
    schema = load_schema("schemas/offers.schema.json")
    payload = {
        "offers": [
            {
                "product_name": "Wine A",
                "price_mxn": 199,
                "discount_text": None,
                "volume_ml": 750,
                "availability": "in_stock",
                "url": "https://example.com/p/wine-a",
                "confidence": 0.9,
            }
        ]
    }
    validate_json(payload, schema)


def test_review_schema_rejects_invalid_payload() -> None:
    schema = load_schema("schemas/review_summary.schema.json")
    bad_payload = {"avg_rating": 10}
    with pytest.raises(ValueError):
        validate_json(bad_payload, schema)

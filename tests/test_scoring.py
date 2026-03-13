"""Unit tests for recommendation scoring logic."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.scoring import is_excluded, score_recommended_buy, score_cheapest_favorite


def test_is_excluded_sweet():
    assert is_excluded({"sweetness": "sweet", "is_grape_wine": True}) is True
    assert is_excluded({"sweetness": "dry", "is_grape_wine": True}) is False


def test_is_excluded_non_grape():
    assert is_excluded({"sweetness": "dry", "is_grape_wine": False}) is True


def test_score_recommended_buy_in_band():
    wine = {"sweetness": "dry", "is_grape_wine": True}
    offer = {"price_mxn": 250, "discount_text": None}
    profile = {}
    agg = None
    score, bullets = score_recommended_buy(wine, offer, profile, agg)
    assert score > 0
    assert "price" in str(bullets).lower() or "target" in str(bullets).lower()


def test_score_cheapest_favorite():
    offer = {"price_mxn": 150}
    score = score_cheapest_favorite(offer)
    assert score > 0

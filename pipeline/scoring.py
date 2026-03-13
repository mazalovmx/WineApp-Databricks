"""Recommendation scoring logic."""
from __future__ import annotations

from typing import Any, Optional

# Hard filters
SWEET_TYPES = {"sweet", "semi-sweet", "semi-sweet", "dulce"}
EXCLUDED_TYPES = {"fruit wine", "mead", "sake", "rice wine"}


def is_excluded(wine: dict[str, Any]) -> bool:
    """Hard exclude: sweet and non-grape wines."""
    if wine.get("is_grape_wine") is False:
        return True
    sweetness = (wine.get("sweetness") or "unknown").lower()
    if sweetness in SWEET_TYPES:
        return True
    wtype = (wine.get("type_") or wine.get("type") or "").lower()
    if wtype in EXCLUDED_TYPES:
        return True
    return False


def score_recommended_buy(
    wine: dict[str, Any],
    offer: dict[str, Any],
    user_profile: dict[str, Any],
    review_agg: Optional[dict[str, Any]],
) -> tuple[float, list[str]]:
    """
    Score a wine/offer for Recommended Buys.
    Returns (score, explanation_bullets).
    """
    if is_excluded(wine):
        return 0.0, []

    price = offer.get("price_mxn") or 0
    if price <= 0:
        return 0.0, []

    # Price score: prefer 100-400 MXN (target band)
    target_low, target_high = 100, 400
    if target_low <= price <= target_high:
        price_score = 1.0
        price_reason = "Within target price range (100–400 MXN)"
    elif price < target_low:
        price_score = 0.85
        price_reason = "Below target band — possible value buy"
    else:
        # Above 400: deprioritize unless "wow deal"
        price_score = max(0, 0.5 - (price - target_high) / 500)
        price_reason = "Above typical budget — consider if exceptional"

    # Discount bonus
    discount_text = (offer.get("discount_text") or "").strip()
    discount_bonus = 0.1 if discount_text and "%" in discount_text else 0
    discount_reason = "Discount available" if discount_bonus else None

    # Review bonus
    review_score = 0.0
    review_reason = None
    if review_agg:
        avg = review_agg.get("avg_rating")
        if avg is not None:
            try:
                r = float(avg)
                if r >= 4:
                    review_score = 0.2
                    review_reason = "Strong reviews"
                elif r >= 3:
                    review_score = 0.1
                    review_reason = "Decent reviews"
            except (TypeError, ValueError):
                pass

    # Descriptor match (simplified)
    desc_match = 0.0
    desc_reason = None
    user_descriptors = set((user_profile.get("descriptors") or {}).keys())
    wine_descriptors = set((review_agg or {}).get("descriptors") or {})
    if user_descriptors and wine_descriptors:
        overlap = len(user_descriptors & wine_descriptors) / max(len(user_descriptors), 1)
        if overlap > 0:
            desc_match = 0.15 * overlap
            desc_reason = "Matches your taste descriptors"

    total = price_score + discount_bonus + review_score + desc_match
    total = min(1.0, total)

    bullets = [r for r in [price_reason, discount_reason, review_reason, desc_reason] if r]
    return round(total, 3), bullets[:4]


def score_cheapest_favorite(
    offer: dict[str, Any],
    delivery_mxn: float = 0,
) -> float:
    """
    For Cheapest Favorites: score = inverse of total price (lower is better).
    We'll sort by total price ascending; this returns a comparable score.
    """
    price = offer.get("price_mxn") or 0
    total = price + delivery_mxn
    if total <= 0:
        return 0.0
    return 1000.0 / total  # Higher score = cheaper

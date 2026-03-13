from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ScoringInput:
    price_mxn: float
    discount_text: str | None
    external_rating: float | None
    descriptor_match: float
    wow_deal: bool
    sweetness: str
    is_grape_wine: bool


def _price_score(price: float) -> float:
    if 100 <= price <= 400:
        return 1.0
    if price < 100:
        return 0.8
    if price <= 550:
        return 0.6
    return 0.2


def _discount_bonus(discount_text: str | None) -> float:
    if not discount_text:
        return 0.0
    return 0.15


def score_offer(payload: ScoringInput) -> float:
    if payload.sweetness == "sweet":
        return -1.0
    if not payload.is_grape_wine:
        return -1.0

    score = 0.0
    score += 0.5 * _price_score(payload.price_mxn)
    score += 0.1 * _discount_bonus(payload.discount_text)
    score += 0.2 * max(0.0, min(payload.descriptor_match, 1.0))
    if payload.external_rating is not None:
        score += 0.2 * max(0.0, min(payload.external_rating / 5.0, 1.0))
    if payload.wow_deal:
        score += 0.15
    return round(score, 4)


def build_explanation(
    locale: str,
    descriptor_match: float,
    price_mxn: float,
    external_rating: float | None,
    conflict_note: str | None,
) -> str:
    is_ru = locale.lower().startswith("ru")
    bullets: list[str] = []
    if descriptor_match >= 0.7:
        bullets.append(
            "• Matches your preferred flavor profile well."
            if not is_ru
            else "• Хорошо совпадает с вашим вкусовым профилем."
        )
    else:
        bullets.append(
            "• Partial taste-profile match."
            if not is_ru
            else "• Частичное совпадение вкусового профиля."
        )
    bullets.append(
        f"• Price/value looks strong at {price_mxn:.0f} MXN."
        if not is_ru
        else f"• Выгодная цена: {price_mxn:.0f} MXN."
    )
    if external_rating is not None:
        bullets.append(
            f"• External reviews average about {external_rating:.1f}/5."
            if not is_ru
            else f"• Внешние отзывы в среднем около {external_rating:.1f}/5."
        )
    if conflict_note:
        bullets.append(
            f"• Review disagreement: {conflict_note}"
            if not is_ru
            else f"• Разногласия в отзывах: {conflict_note}"
        )
    return "\n".join(bullets[:4])

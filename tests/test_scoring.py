from app.scoring import ScoringInput, build_explanation, score_offer


def test_score_offer_prefers_target_price_band() -> None:
    mid = score_offer(
        ScoringInput(
            price_mxn=220,
            discount_text=None,
            external_rating=4.0,
            descriptor_match=0.8,
            wow_deal=False,
            sweetness="dry",
            is_grape_wine=True,
        )
    )
    high = score_offer(
        ScoringInput(
            price_mxn=700,
            discount_text=None,
            external_rating=4.0,
            descriptor_match=0.8,
            wow_deal=False,
            sweetness="dry",
            is_grape_wine=True,
        )
    )
    assert mid > high


def test_score_offer_rejects_sweet_and_non_grape() -> None:
    sweet = score_offer(
        ScoringInput(
            price_mxn=120,
            discount_text=None,
            external_rating=4.0,
            descriptor_match=0.8,
            wow_deal=True,
            sweetness="sweet",
            is_grape_wine=True,
        )
    )
    non_grape = score_offer(
        ScoringInput(
            price_mxn=120,
            discount_text=None,
            external_rating=4.0,
            descriptor_match=0.8,
            wow_deal=True,
            sweetness="dry",
            is_grape_wine=False,
        )
    )
    assert sweet < 0
    assert non_grape < 0


def test_score_offer_rewards_wow_deal_and_discount() -> None:
    base = score_offer(
        ScoringInput(
            price_mxn=180,
            discount_text=None,
            external_rating=4.0,
            descriptor_match=0.7,
            wow_deal=False,
            sweetness="dry",
            is_grape_wine=True,
        )
    )
    boosted = score_offer(
        ScoringInput(
            price_mxn=120,
            discount_text="discount:-15%",
            external_rating=4.0,
            descriptor_match=0.7,
            wow_deal=True,
            sweetness="dry",
            is_grape_wine=True,
        )
    )
    assert boosted > base


def test_build_explanation_includes_conflict_and_locale() -> None:
    en = build_explanation(
        locale="en",
        descriptor_match=0.8,
        price_mxn=199,
        external_rating=4.2,
        conflict_note="mixed finish ratings",
    )
    ru = build_explanation(
        locale="ru",
        descriptor_match=0.4,
        price_mxn=219,
        external_rating=None,
        conflict_note=None,
    )
    assert "mixed finish ratings" in en
    assert "MXN" in en
    assert "вкусового профиля" in ru
    assert "Выгодная цена" in ru

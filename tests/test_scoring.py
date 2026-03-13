from app.scoring import ScoringInput, score_offer


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

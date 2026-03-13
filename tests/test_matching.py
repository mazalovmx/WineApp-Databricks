from app.matching import match_listed_wine, normalize_name, token_overlap


def test_normalize_name_removes_symbols_and_case() -> None:
    assert normalize_name("  Cásîlléro! del Diablo  ") == "casillero del diablo"


def test_token_overlap_higher_for_related_names() -> None:
    a = "Casillero del Diablo Cabernet"
    b = "Casillero del Diablo Merlot"
    c = "Whisky Honey Blend"
    assert token_overlap(a, b) > token_overlap(a, c)


def test_match_listed_wine_returns_confident_match() -> None:
    result = match_listed_wine(
        "Trapiche Malbec Reserve",
        [(1, "Trapiche Malbec Reserve"), (2, "JP Chenet Merlot")],
    )
    assert result.wine_id == 1
    assert result.confidence >= 0.85


def test_match_listed_wine_returns_none_for_unrelated_candidates() -> None:
    result = match_listed_wine(
        "Agave Spirit Reposado",
        [(1, "Casillero Cabernet"), (2, "Trapiche Malbec")],
    )
    assert result.wine_id is None
    assert result.reason == "low_confidence"

"""Unit tests for deduplication helpers."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.deduplication import normalize_name, fuzzy_match_score


def test_normalize_name():
    assert normalize_name("  Vino   Tinto  ") == "vino tinto"
    assert normalize_name("") == ""


def test_fuzzy_match_score_exact():
    assert fuzzy_match_score("Vino Tinto", "vino tinto") == 1.0


def test_fuzzy_match_score_overlap():
    s = fuzzy_match_score("Vino Tinto Tempranillo", "Vino Tinto")
    assert s > 0.5
    assert s <= 1.0


def test_fuzzy_match_score_no_overlap():
    assert fuzzy_match_score("Red Wine", "Beer Lager") < 0.5

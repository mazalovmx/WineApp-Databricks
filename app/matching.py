from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


def normalize_name(name: str) -> str:
    text = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def token_overlap(a: str, b: str) -> float:
    a_set = set(normalize_name(a).split())
    b_set = set(normalize_name(b).split())
    if not a_set or not b_set:
        return 0.0
    intersection = len(a_set & b_set)
    union = len(a_set | b_set)
    return intersection / union


@dataclass(slots=True)
class MatchResult:
    wine_id: int | None
    confidence: float
    reason: str


def match_listed_wine(listed_name: str, candidates: list[tuple[int, str]]) -> MatchResult:
    best_id: int | None = None
    best_score = 0.0

    for wine_id, canonical in candidates:
        score = token_overlap(listed_name, canonical)
        if score > best_score:
            best_score = score
            best_id = wine_id

    if best_score >= 0.85:
        return MatchResult(wine_id=best_id, confidence=best_score, reason="high_overlap")
    if best_score >= 0.6:
        return MatchResult(wine_id=best_id, confidence=best_score, reason="medium_overlap")
    return MatchResult(wine_id=None, confidence=best_score, reason="low_confidence")

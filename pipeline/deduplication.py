"""Deduplication and wine entity matching."""
from __future__ import annotations

import re
from typing import Any, Optional

from sqlalchemy.orm import Session

# Use backend LLM if available
try:
    from backend.src.llm.factory import get_llm_client
    HAS_LLM = True
except ImportError:
    HAS_LLM = False


def normalize_name(name: str) -> str:
    """Normalize wine name for matching: lowercase, collapse whitespace, remove accents."""
    if not name:
        return ""
    # Basic normalization - extend for accents if needed
    s = name.lower().strip()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^\w\s\-']", "", s)  # Remove punctuation except hyphen/apostrophe
    return s


def fuzzy_match_score(a: str, b: str) -> float:
    """
    Simple heuristic match score 0-1.
    Uses normalized names and checks containment / word overlap.
    """
    na, nb = normalize_name(a), normalize_name(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    # Word overlap
    wa, wb = set(na.split()), set(nb.split())
    if not wa or not wb:
        return 0.0
    overlap = len(wa & wb) / max(len(wa), len(wb))
    # Bonus for one containing the other
    if na in nb or nb in na:
        overlap = min(1.0, overlap + 0.2)
    return round(overlap, 3)


def match_listed_name_to_wines(
    session: Session,
    listed_name: str,
    candidates: list[dict[str, Any]],
    use_llm: bool = False,
) -> Optional[dict[str, Any]]:
    """
    Match a store listing name to a canonical wine.
    Returns dict with wine_id, confidence, or None if no match.
    """
    if not candidates:
        return None

    # Heuristic: pick best candidate by fuzzy score
    best: Optional[tuple[float, dict]] = None
    for c in candidates:
        score = fuzzy_match_score(listed_name, c.get("canonical_name", ""))
        if score > 0.5 and (best is None or score > best[0]):
            best = (score, c)

    if best and best[0] >= 0.6:
        return {
            "wine_id": best[1]["id"],
            "confidence": best[0],
            "method": "heuristic",
        }

    if use_llm and HAS_LLM:
        try:
            client = get_llm_client()
            result = client.match_wine_entity(listed_name, candidates)
            if result and result.get("wine_id") and result.get("confidence", 0) >= 0.5:
                return result
        except Exception:
            pass

    return None

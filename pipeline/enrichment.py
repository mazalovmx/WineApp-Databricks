"""External review enrichment for wines."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from pipeline.db import get_engine
from pipeline.llm_facade import get_llm_client
from pipeline.storage import get_storage
from pipeline import config

# Import models - adjust path if needed
try:
    from backend.src.models import Wine, ExternalReview, ReviewAggregate
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from backend.src.models import Wine, ExternalReview, ReviewAggregate


def enrich_wine_reviews(
    session: Session,
    wine_id: int,
    wine_name: str,
    max_review_snippets: int = 5,
    skip_if_recent: bool = True,
    llm_quota_remaining: list[int],
) -> bool:
    """
    Enrich a wine with external reviews via LLM web search + summarization.
    Modifies llm_quota_remaining in place (decrements on use).
    Returns True if enrichment was performed.
    """
    if llm_quota_remaining[0] <= 0:
        return False

    # Optional: skip if we enriched recently
    existing = (
        session.query(ExternalReview)
        .filter(ExternalReview.wine_id == wine_id)
        .order_by(ExternalReview.fetched_at.desc())
        .first()
    )
    if skip_if_recent and existing:
        # Could check fetched_at age here
        pass

    client = get_llm_client()
    quota = llm_quota_remaining[0]

    # 1. Search for reviews
    if quota <= 0:
        return False
    query = f'"{wine_name}" wine review rating'
    results = client.search(query)
    llm_quota_remaining[0] -= 1

    if not results or not results.get("urls"):
        return False

    # 2. Summarize (mock: we'd fetch pages and summarize; for MVP use placeholder)
    texts = results.get("snippets", [])[:max_review_snippets]
    if not texts:
        texts = [f"Search results for {wine_name}"]

    if quota <= 0:
        return False
    summary = client.summarize_reviews(texts)
    llm_quota_remaining[0] -= 1

    if not summary:
        return False

    # Store external review record
    raw_ref = None
    storage = get_storage()
    if storage:
        raw_ref = f"reviews/wine_{wine_id}/search_{results.get('query_id', 'x')}.json"
        storage.put_json(raw_ref, {"query": query, "snippets": texts, "urls": results.get("urls", [])})

    rev = ExternalReview(
        wine_id=wine_id,
        source_name="web_search",
        source_url=results.get("urls", [""])[0] if results.get("urls") else None,
        fetched_at=config.utc_now(),
        raw_ref=raw_ref,
        extracted_json=summary if isinstance(summary, dict) else {"summary": str(summary)},
    )
    session.add(rev)

    # Upsert review_aggregates
    agg = session.query(ReviewAggregate).filter(ReviewAggregate.wine_id == wine_id).first()
    if not agg:
        agg = ReviewAggregate(wine_id=wine_id)
        session.add(agg)

    agg.avg_rating = summary.get("avg_rating")
    agg.rating_scale = summary.get("rating_scale", "1-5")
    agg.descriptors = summary.get("descriptors", {})
    agg.pros = summary.get("pros", [])
    agg.cons = summary.get("cons", [])
    agg.disagreement_summary = summary.get("disagreement_summary")
    agg.updated_at = config.utc_now()

    session.commit()
    return True

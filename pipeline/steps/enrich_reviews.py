"""Enrich wines with external reviews (LLM web search + summarization)."""
from typing import List


def run(session, wines: List[dict]) -> None:
    """
    For each wine, optionally fetch external reviews and store aggregates.
    MVP: skip enrichment to stay within LLM quota; placeholder implementation.
    """
    # Quota control: max 5 wines enriched per run for MVP
    max_enrich = min(5, len(wines) if wines else 0)
    if max_enrich == 0:
        return
    # Placeholder: actual enrichment would call LLM search + summarize
    # and populate external_reviews + review_aggregates
    pass

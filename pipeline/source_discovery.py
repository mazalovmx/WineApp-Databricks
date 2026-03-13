"""Source discovery - find relevant store/product listing URLs."""
import json
import os
from pathlib import Path
from typing import List

from .db import get_session
from .storage import StorageBackend
from .llm_facade import get_llm_client
from ..backend.src.models import Store


def load_seed_sources() -> List[dict]:
    """Load configured seed sources from data/sources.json if it exists."""
    path = Path(__file__).parent.parent / "data" / "sources.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []


async def discover_sources(llm_search=True) -> List[dict]:
    """
    Discover or refresh store/product page URLs.
    Uses seed sources by default; optionally uses LLM web search to find more.
    """
    seed = load_seed_sources()
    if not seed and llm_search:
        client = get_llm_client()
        results = await client.search(
            "wine shops supermarkets Guadalajara Jalisco product listings"
        )
        # Parse results into source format
        return [
            {"name": r.get("title", "Unknown"), "url": r.get("url", ""), "category": "unknown"}
            for r in (results.results or [])[:20]
        ]
    return seed

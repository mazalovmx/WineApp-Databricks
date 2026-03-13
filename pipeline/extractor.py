"""Extract structured wine offers from page content."""
import json
import logging
from pathlib import Path

from .llm_facade import get_llm_client

logger = logging.getLogger(__name__)

SCHEMA_PATH = Path(__file__).parent.parent / "prompts" / "extract_offers_schema.json"


def load_schema() -> dict:
    with open(SCHEMA_PATH) as f:
        return json.load(f)


async def extract_offers_from_page(page_text: str, store_name: str) -> list[dict]:
    """
    Use LLM to extract wine offers from page HTML/text.
    Returns list of offer dicts matching extract_offers_schema.
    """
    client = get_llm_client()
    schema = load_schema()
    result = await client.extract_offers(page_text, schema, store_name=store_name)
    if isinstance(result, dict) and "offers" in result:
        return result["offers"]
    if isinstance(result, list):
        return result
    return []

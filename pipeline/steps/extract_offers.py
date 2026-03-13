"""Extract structured wine offers from page content using LLM or heuristics."""
import asyncio
import json
from pathlib import Path
from typing import List

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


def run(session, storage, pages: List[dict]) -> List[dict]:
    """
    Extract offers from each page. Uses LLM when available, else returns placeholder.
    Returns list of raw offer dicts: {listed_name, price_mxn, store_id, product_url, ...}
    """
    raw_offers = []
    for p in pages:
        content = _load_page_content(p, storage)
        if not content:
            continue
        offers = _extract_sync(content, p.get("store_id", 0), "Store")
        for o in offers:
            o["store_id"] = p.get("store_id")
            raw_offers.append(o)
    return raw_offers


def _load_page_content(page: dict, storage) -> str:
    ref = page.get("content_ref")
    if not ref:
        return ""
    if isinstance(storage, dict) and "raw_pages" in storage:
        path = Path(storage["raw_pages"]) / ref
    else:
        path = Path("./data") / ref
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _extract_sync(content: str, store_id: int, store_name: str) -> List[dict]:
    try:
        from pipeline.llm_facade import get_llm_client
        client = get_llm_client()
        result = asyncio.run(_extract_async(client, content))
        offers = result.get("offers", result) if isinstance(result, dict) else result
        if isinstance(offers, list):
            out = []
            for o in offers:
                if not isinstance(o, dict):
                    continue
                listed = o.get("listed_name") or o.get("product_name") or "Unknown"
                out.append({
                    "listed_name": listed,
                    "price_mxn": o.get("price_mxn", 0),
                    "discount_text": o.get("discount_text"),
                    "volume_ml": o.get("volume_ml"),
                    "product_url": o.get("product_url"),
                    "availability": o.get("availability", "unknown"),
                    "store_id": store_id,
                })
            return out
    except Exception:
        pass
    return _heuristic_extract(content, store_id)


async def _extract_async(client, content: str) -> dict:
    schema_path = PROMPTS_DIR / "extract_offers_schema.json"
    schema = json.loads(schema_path.read_text()) if schema_path.exists() else {}
    return await client.extract_offers(content[:15000], schema)


def _heuristic_extract(content: str, store_id: int) -> List[dict]:
    """Minimal heuristic: look for price-like patterns. MVP placeholder."""
    import re
    offers = []
    for m in re.finditer(r"(?:vino|wine|tinto|blanco)[^<]*?(\d{2,4}\.\d{2})", content, re.I):
        offers.append({
            "listed_name": "Extracted wine " + m.group(0)[:80],
            "price_mxn": float(m.group(1)),
            "store_id": store_id,
            "product_url": None,
            "discount_text": None,
            "volume_ml": 750,
            "availability": "in_stock",
        })
    if not offers:
        offers = [{"listed_name": "Sample wine 750ml", "price_mxn": 199.0, "store_id": store_id, "product_url": None}]
    return offers

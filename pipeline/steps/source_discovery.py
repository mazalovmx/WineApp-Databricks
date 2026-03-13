"""Source discovery - find/store relevant store/product listing URLs."""
import json
from pathlib import Path
from typing import Any, List

# Seed sources for Guadalajara wine stores (MVP - controlled list)
DEFAULT_SEED_SOURCES = [
    {"name": "La Playa", "url": "https://laplaya.com.mx/vinos", "category": "specialty"},
    {"name": "Vinos Américas", "url": "https://vinosamericas.com/catalogo", "category": "specialty"},
]


def run(session, storage) -> List[dict]:
    """
    Load or discover store sources. Returns list of store dicts with id/name/url/category.
    Uses seed sources from data/sources.json or DEFAULT_SEED_SOURCES.
    """
    seed_path = Path(__file__).resolve().parents[2] / "data" / "sources.json"
    if seed_path.exists():
        with open(seed_path) as f:
            sources = json.load(f)
    else:
        sources = DEFAULT_SEED_SOURCES

    # Ensure stores exist in DB
    from sqlalchemy import text
    for s in sources:
        existing = session.execute(
            text("SELECT id FROM stores WHERE name = :name LIMIT 1"),
            {"name": s["name"]},
        ).fetchone()
        if not existing:
            session.execute(
                text("""
                    INSERT INTO stores (name, category, base_url, enabled)
                    VALUES (:name, :cat, :url, true)
                """),
                {"name": s["name"], "cat": s.get("category", "specialty"), "url": s.get("url", "")},
            )
    session.commit()

    result = session.execute(text("SELECT id, name, base_url, category FROM stores WHERE enabled = true"))
    rows = result.fetchall()
    return [{"id": r[0], "name": r[1], "url": r[2] or "", "category": r[3]} for r in rows]

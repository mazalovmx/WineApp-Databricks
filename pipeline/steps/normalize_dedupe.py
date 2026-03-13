"""Normalize offers and deduplicate into canonical wines."""
from datetime import datetime
from typing import List, Tuple

from pipeline.deduplication import normalize_name, fuzzy_match_score


def run(session, raw_offers: List[dict]) -> Tuple[List[dict], List[dict]]:
    """
    Map raw offers to canonical wines. Create wines as needed, dedupe by name.
    Returns (wines_list, offers_list) with wine_id set on offers.
    """
    from sqlalchemy import text
    wines_created = {}
    offers_out = []

    for o in raw_offers:
        listed_name = (o.get("listed_name") or "").strip()
        if not listed_name:
            continue

        price = float(o.get("price_mxn") or 0)
        store_id = int(o.get("store_id") or 0)
        product_url = o.get("product_url")

        # Find or create canonical wine
        norm = normalize_name(listed_name)
        wine_id = wines_created.get(norm)
        if wine_id is None:
            r2 = session.execute(text("SELECT id FROM wines WHERE canonical_name = :name LIMIT 1"), {"name": listed_name[:300]})
            row = r2.fetchone()
            if row:
                wine_id = row[0]
            else:
                r = session.execute(
                    text("""
                        INSERT INTO wines (canonical_name, sweetness, is_grape_wine, created_at, updated_at)
                        VALUES (:name, 'unknown', true, :now, :now)
                        RETURNING id
                    """),
                    {"name": listed_name[:300], "now": datetime.utcnow()},
                )
                wine_id = r.scalar()
            if wine_id:
                wines_created[norm] = wine_id

        if wine_id:
            r = session.execute(
                text("""
                    INSERT INTO offers (store_id, wine_id, listed_name, price_mxn, product_url, captured_at)
                    VALUES (:sid, :wid, :name, :price, :url, :now)
                    RETURNING id
                """),
                {"sid": store_id, "wid": wine_id, "name": listed_name[:500], "price": price, "url": product_url, "now": datetime.utcnow()},
            )
            session.commit()

    wines = [{"id": v} for v in wines_created.values()]
    return wines, offers_out

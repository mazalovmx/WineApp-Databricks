"""Score and rank recommendations per user."""
from sqlalchemy import text
from typing import List


def run(session) -> List[dict]:
    """
    Generate recommended_buys and cheapest_favorites for each user.
    Returns list of recommendation dicts: {user_id, kind, rank, wine_id, offer_id, score, explanation}.
    """
    recs = []
    users = session.execute(text("SELECT id FROM users")).fetchall()
    if not users:
        return recs

    for (user_id,) in users:
        # Recommended Buys: wines not yet tried, in price band 100-400 MXN
        r = session.execute(
            text("""
                SELECT o.id as offer_id, o.wine_id, o.price_mxn
                FROM offers o
                JOIN wines w ON w.id = o.wine_id
                WHERE o.wine_id NOT IN (SELECT wine_id FROM user_ratings WHERE user_id = :uid)
                  AND w.is_grape_wine = true
                  AND (w.sweetness IS NULL OR w.sweetness NOT IN ('sweet', 'semi-sweet'))
                  AND o.price_mxn BETWEEN 100 AND 400
                ORDER BY o.price_mxn ASC
                LIMIT 10
            """),
            {"uid": user_id},
        )
        for rank, row in enumerate(r, 1):
            recs.append({
                "user_id": user_id,
                "kind": "recommended_buys",
                "rank": rank,
                "wine_id": row[1],
                "offer_id": row[0],
                "score": 100.0 / max(1, row[2]),
                "explanation": "Within target price range and matches dry grape wine criteria.",
            })

        # Cheapest Favorites: wines rated >=4, sorted by current price
        r2 = session.execute(
            text("""
                SELECT o.id as offer_id, o.wine_id, o.price_mxn
                FROM offers o
                JOIN user_ratings ur ON ur.wine_id = o.wine_id AND ur.user_id = :uid
                WHERE ur.rating_1_5 >= 4
                ORDER BY o.price_mxn ASC
                LIMIT 10
            """),
            {"uid": user_id},
        )
        for rank, row in enumerate(r2, 1):
            recs.append({
                "user_id": user_id,
                "kind": "cheapest_favorites",
                "rank": rank,
                "wine_id": row[1],
                "offer_id": row[0],
                "score": 1000.0 / max(1, row[2]),
                "explanation": "You liked this wine; here's the cheapest current offer.",
            })

    return recs

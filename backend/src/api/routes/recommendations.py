"""Recommendation endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from backend.src.db import get_session
from backend.src.auth import get_current_user

router = APIRouter(tags=["recommendations"])


@router.get("/recommendations")
def get_recommendations(
    kind: str | None = Query(None, description="recommended_buys | cheapest_favorites"),
    date: str | None = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Get recommendations for current user."""
    user_id = current_user["sub"]
    locale = current_user.get("locale", "en")

    with get_session() as session:
        q = """
            SELECT r.kind, r.rank, r.wine_id, r.offer_id, r.score, r.explanation,
                   w.canonical_name, o.price_mxn, o.product_url, s.name as store_name
            FROM recommendations r
            JOIN wines w ON w.id = r.wine_id
            LEFT JOIN offers o ON o.id = r.offer_id
            LEFT JOIN stores s ON s.id = o.store_id
            JOIN recommendation_runs rr ON rr.id = r.run_id
            WHERE r.user_id = :uid AND rr.status = 'success'
        """
        params = {"uid": user_id}
        if kind:
            q += " AND r.kind = :kind"
            params["kind"] = kind
        q += " ORDER BY r.kind, r.rank"

        rows = session.execute(text(q), params).fetchall()

    return [
        {
            "kind": r[0],
            "rank": r[1],
            "wine_id": r[2],
            "offer_id": r[3],
            "score": float(r[4]) if r[4] else None,
            "explanation": r[5],
            "wine_name": r[6],
            "price_mxn": float(r[7]) if r[7] else None,
            "product_url": r[8],
            "store_name": r[9],
        }
        for r in rows
    ]


@router.get("/favorites/cheapest")
def cheapest_favorites(current_user: dict = Depends(get_current_user)):
    """Alias for recommendations?kind=cheapest_favorites."""
    return get_recommendations(kind="cheapest_favorites", current_user=current_user)

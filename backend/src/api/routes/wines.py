"""Wines and tried-wines search endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from backend.src.db import get_session
from backend.src.auth import get_current_user

router = APIRouter(prefix="/wines", tags=["wines"])


@router.get("/tried")
def get_tried_wines(
    query: str | None = Query(None),
    wine_type: str | None = Query(None, description="red|white|rose|sparkling"),
    current_user: dict = Depends(get_current_user),
):
    """Search tried wines with filters."""
    user_id = current_user["sub"]

    with get_session() as session:
        q = """
            SELECT w.id, w.canonical_name, w.type, w.grapes, ur.rating_1_5, ur.comment, ur.tried_at, ur.created_at
            FROM user_ratings ur
            JOIN wines w ON w.id = ur.wine_id
            WHERE ur.user_id = :uid
        """
        params = {"uid": user_id}
        if query:
            q += " AND w.canonical_name ILIKE :q"
            params["q"] = f"%{query}%"
        if wine_type:
            q += " AND w.type = :wtype"
            params["wtype"] = wine_type
        q += " ORDER BY ur.created_at DESC"

        rows = session.execute(text(q), params).fetchall()

    return [
        {
            "wine_id": r[0],
            "wine_name": r[1],
            "type": r[2],
            "grapes": r[3],
            "rating": r[4],
            "comment": r[5],
            "tried_at": r[6].isoformat() if r[6] else None,
            "rated_at": r[7].isoformat() if r[7] else None,
        }
        for r in rows
    ]

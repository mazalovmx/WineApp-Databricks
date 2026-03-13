"""Rating submission endpoint."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from backend.src.db import get_session
from backend.src.auth import get_current_user

router = APIRouter(tags=["ratings"])


class RatingSubmission(BaseModel):
    wine_id: int
    rating_1_5: int
    comment: str | None = None
    tried_at: datetime | None = None


@router.post("/ratings")
def submit_rating(
    body: RatingSubmission,
    current_user: dict = Depends(get_current_user),
):
    """Submit or update rating for a wine."""
    if not 1 <= body.rating_1_5 <= 5:
        raise HTTPException(status_code=400, detail="rating_1_5 must be 1-5")
    user_id = current_user["sub"]

    with get_session() as session:
        # Delete existing rating for this user+wine, then insert
        session.execute(
            text("DELETE FROM user_ratings WHERE user_id = :uid AND wine_id = :wid"),
            {"uid": user_id, "wid": body.wine_id},
        )
        session.execute(
            text("""
                INSERT INTO user_ratings (user_id, wine_id, rating_1_5, comment, tried_at)
                VALUES (:uid, :wid, :rating, :comment, :tried)
            """),
            {
                "uid": user_id,
                "wid": body.wine_id,
                "rating": body.rating_1_5,
                "comment": body.comment,
                "tried": body.tried_at or datetime.utcnow(),
            },
        )

    return {"ok": True, "wine_id": body.wine_id}

"""Write recommendation outputs to recommendations table."""
from datetime import datetime
from typing import List


def run(session, run_id: int, recommendations: List[dict]) -> None:
    """
    Insert recommendation records for the given run.
    """
    from sqlalchemy import text
    for rec in recommendations:
        session.execute(
            text("""
                INSERT INTO recommendations (run_id, user_id, kind, rank, wine_id, offer_id, score, explanation)
                VALUES (:run_id, :user_id, :kind, :rank, :wine_id, :offer_id, :score, :explanation)
            """),
            {
                "run_id": run_id,
                "user_id": rec["user_id"],
                "kind": rec["kind"],
                "rank": rec["rank"],
                "wine_id": rec["wine_id"],
                "offer_id": rec.get("offer_id"),
                "score": rec.get("score"),
                "explanation": rec.get("explanation", ""),
            },
        )
    session.commit()

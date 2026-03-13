"""Health and status endpoints."""
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import text
from backend.src.db import get_session

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    """Status + last successful run timestamp."""
    try:
        with get_session() as session:
            r = session.execute(
                text("""
                    SELECT finished_at FROM recommendation_runs
                    WHERE status = 'success' ORDER BY finished_at DESC LIMIT 1
                """)
            ).fetchone()
            last_run = r[0] if r else None
    except Exception:
        last_run = None
    return {
        "status": "ok",
        "last_successful_run": last_run.isoformat() if last_run else None,
    }

"""
Batch pipeline runner for Guadalajara Wine Finder.
Runs: discover -> fetch -> extract -> dedupe -> enrich -> score -> write outputs.
"""
import os
import sys
from pathlib import Path

# Add workspace root for backend and pipeline imports
_workspace = Path(__file__).resolve().parent.parent
if str(_workspace) not in sys.path:
    sys.path.insert(0, str(_workspace))

from pipeline.steps import (
    source_discovery,
    fetch_pages,
    extract_offers,
    normalize_dedupe,
    enrich_reviews,
    score_recommendations,
    write_outputs,
)
from pipeline.db import get_session, init_db
from pipeline.storage import init_storage
import structlog

logger = structlog.get_logger()


def run(mode: str = "daily"):
    """Execute full pipeline."""
    run_id = None
    try:
        init_db()
        storage = init_storage()
        run_id = _create_run(mode)

        with get_session() as session:
            # 1. Source discovery
            stores = source_discovery.run(session, storage)
            logger.info("source_discovery_done", store_count=len(stores))

            # 2. Fetch pages
            pages = fetch_pages.run(session, storage, stores)
            logger.info("fetch_pages_done", page_count=len(pages))

            # 3. Extract offers
            raw_offers = extract_offers.run(session, storage, pages)
            logger.info("extract_offers_done", offer_count=len(raw_offers))

            # 4. Normalize & dedupe
            wines, offers = normalize_dedupe.run(session, raw_offers)
            logger.info("normalize_dedupe_done", wine_count=len(wines), offer_count=len(offers))

            # 5. Enrich with external reviews
            enrich_reviews.run(session, wines)
            logger.info("enrich_reviews_done")

            # 6. Score & rank recommendations
            recommendations = score_recommendations.run(session)
            logger.info("score_recommendations_done", rec_count=len(recommendations))

            # 7. Write outputs
            write_outputs.run(session, run_id, recommendations)
            logger.info("write_outputs_done")

        _complete_run(run_id, "success")
        return 0
    except Exception as e:
        logger.exception("pipeline_failed", error=str(e))
        if run_id:
            _complete_run(run_id, "fail")
        return 1


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "daily"
    sys.exit(run(mode))


def _create_run(mode: str):
    from sqlalchemy import text
    from datetime import datetime
    with get_session() as session:
        r = session.execute(
            text("""
                INSERT INTO recommendation_runs (mode, started_at, status)
                VALUES (:mode, :started, 'running')
                RETURNING id
            """),
            {"mode": mode, "started": datetime.utcnow()},
        )
        return r.scalar()


def _complete_run(run_id: int, status: str):
    from sqlalchemy import text
    from datetime import datetime
    with get_session() as session:
        session.execute(
            text("""
                UPDATE recommendation_runs
                SET finished_at = :finished, status = :status
                WHERE id = :id
            """),
            {"finished": datetime.utcnow(), "status": status, "id": run_id},
        )
        session.commit()

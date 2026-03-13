from pathlib import Path

from sqlalchemy.orm import Session

from app.db import engine
from app.models import Recommendation, RecommendationRun
from app.pipeline import run_pipeline


def test_pipeline_run_creates_outputs() -> None:
    with Session(engine) as session:
        result = run_pipeline(session, mode="manual")
        run = session.get(RecommendationRun, result.run_id)
        assert run is not None
        assert run.status == "success"
        assert Path(run.logs_ref).exists()

        rec_count = session.query(Recommendation).filter(Recommendation.run_id == result.run_id).count()
        assert rec_count >= 1


def test_pipeline_can_run_twice_without_raw_page_conflict() -> None:
    with Session(engine) as session:
        first = run_pipeline(session, mode="manual")
        second = run_pipeline(session, mode="manual")
        assert first.status == "success"
        assert second.status == "success"

        run = session.get(RecommendationRun, second.run_id)
        assert run is not None
        assert Path(run.logs_ref).exists()

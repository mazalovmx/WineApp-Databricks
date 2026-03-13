from __future__ import annotations

from datetime import timedelta

from sqlalchemy.orm import Session

from app.db import engine
from app.models import RecommendationRun, ReviewAggregate, UserRating, Wine
from app.pipeline import _descriptor_match, latest_run_query
from app.time_utils import utc_now_naive


def _add_wine(session: Session, name: str) -> Wine:
    wine = Wine(canonical_name=name, sweetness="dry", is_grape_wine=True)
    session.add(wine)
    session.flush()
    return wine


def test_descriptor_match_defaults_when_user_has_no_liked_wines() -> None:
    with Session(engine) as session:
        target = _add_wine(session, "Target Wine")
        session.commit()
        score = _descriptor_match(session, target.id, "A")
        assert score == 0.65


def test_descriptor_match_uses_overlap_and_fallback_paths() -> None:
    with Session(engine) as session:
        liked = _add_wine(session, "Liked Wine")
        target = _add_wine(session, "Target Wine")
        session.add(
            UserRating(
                user_id="A",
                wine_id=liked.id,
                rating_1_5=5,
                comment="liked",
                tried_at=utc_now_naive(),
            )
        )
        session.commit()

        # User has liked wines but target has no review aggregate.
        assert _descriptor_match(session, target.id, "A") == 0.5

        session.merge(
            ReviewAggregate(
                wine_id=target.id,
                avg_rating=4.0,
                rating_scale="5",
                descriptors={"items": []},
                pros=[],
                cons=[],
                disagreement_summary=None,
            )
        )
        session.commit()
        # Target has aggregate but no tags.
        assert _descriptor_match(session, target.id, "A") == 0.55

        session.merge(
            ReviewAggregate(
                wine_id=target.id,
                avg_rating=4.0,
                rating_scale="5",
                descriptors={"items": [{"tag": "fruity"}]},
                pros=[],
                cons=[],
                disagreement_summary=None,
            )
        )
        session.commit()
        # Liked wine has no descriptors, so liked-tags fallback applies.
        assert _descriptor_match(session, target.id, "A") == 0.6

        session.merge(
            ReviewAggregate(
                wine_id=liked.id,
                avg_rating=4.2,
                rating_scale="5",
                descriptors={"items": [{"tag": "fruity"}]},
                pros=[],
                cons=[],
                disagreement_summary=None,
            )
        )
        session.commit()
        # Exact descriptor overlap.
        assert _descriptor_match(session, target.id, "A") == 1.0


def test_latest_run_query_filters_success() -> None:
    with Session(engine) as session:
        session.add_all(
            [
                RecommendationRun(
                    id="run-failed",
                    mode="manual",
                    started_at=utc_now_naive() - timedelta(minutes=2),
                    finished_at=utc_now_naive() - timedelta(minutes=1),
                    status="fail",
                    logs_ref="artifacts/run-failed/run_summary.json",
                ),
                RecommendationRun(
                    id="run-success",
                    mode="manual",
                    started_at=utc_now_naive() - timedelta(minutes=1),
                    finished_at=utc_now_naive(),
                    status="success",
                    logs_ref="artifacts/run-success/run_summary.json",
                ),
            ]
        )
        session.commit()

        success_rows = session.execute(latest_run_query(success_only=True)).scalars().all()
        assert len(success_rows) == 1
        assert success_rows[0].id == "run-success"

        all_rows = session.execute(latest_run_query(success_only=False)).scalars().all()
        assert len(all_rows) == 2

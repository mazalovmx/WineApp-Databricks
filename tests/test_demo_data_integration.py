from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import engine
from app.demo_data import seed_demo_data
from app.models import Offer, Recommendation, RecommendationRun, UserRating, Wine


def test_seed_demo_data_populates_functional_dataset() -> None:
    with Session(engine) as session:
        summary = seed_demo_data(session, total_wines=45, reset=True, run_pipeline_after_seed=True)
        assert summary.demo_wines == 45
        assert summary.demo_offers >= 90
        assert summary.ratings_a >= 20
        assert summary.ratings_b >= 10
        assert summary.run_id is not None

        # Verify recommendation run exists and has outputs.
        run = session.get(RecommendationRun, summary.run_id)
        assert run is not None
        rec_count = session.execute(
            select(Recommendation).where(Recommendation.run_id == summary.run_id)
        ).scalars().all()
        assert len(rec_count) > 0

        # Verify demo types/sweetness diversity exists for filter and hard-rule testing.
        demo_wines = session.execute(
            select(Wine).where(Wine.canonical_name.like("Demo Wine%"))
        ).scalars().all()
        assert any(w.type == "red" for w in demo_wines)
        assert any(w.type == "white" for w in demo_wines)
        assert any(w.sweetness == "sweet" for w in demo_wines)
        assert any(not w.is_grape_wine for w in demo_wines)

        demo_offers = session.execute(
            select(Offer).join(Wine, Wine.id == Offer.wine_id).where(Wine.canonical_name.like("Demo Wine%"))
        ).scalars().all()
        assert any(offer.discount_text is not None for offer in demo_offers)
        assert any(offer.availability == "unknown" for offer in demo_offers)

        ratings = session.execute(
            select(UserRating).join(Wine, Wine.id == UserRating.wine_id).where(Wine.canonical_name.like("Demo Wine%"))
        ).scalars().all()
        assert any(r.user_id == "A" for r in ratings)
        assert any(r.user_id == "B" for r in ratings)


def test_seed_demo_data_reset_prevents_duplication() -> None:
    with Session(engine) as session:
        first = seed_demo_data(session, total_wines=42, reset=True, run_pipeline_after_seed=False)
        second = seed_demo_data(session, total_wines=42, reset=True, run_pipeline_after_seed=False)
        assert first.demo_wines == 42
        assert second.demo_wines == 42
        assert second.demo_offers == first.demo_offers

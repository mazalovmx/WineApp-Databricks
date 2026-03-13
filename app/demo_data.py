from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import (
    ExternalReview,
    Offer,
    PriceHistory,
    Recommendation,
    RecommendationRun,
    ReviewAggregate,
    Store,
    UserRating,
    Wine,
)
from app.pipeline import run_pipeline

DEMO_STORE_PREFIX = "Demo Store"
DEMO_WINE_PREFIX = "Demo Wine"


@dataclass(slots=True)
class DemoSeedSummary:
    demo_wines: int
    demo_offers: int
    ratings_a: int
    ratings_b: int
    run_id: str | None


def _demo_wine_name(index: int) -> str:
    regions = [
        "Valle",
        "Sierra",
        "Costa",
        "Altos",
        "Norte",
        "Sur",
        "Central",
        "Ribera",
        "Montes",
    ]
    grapes = [
        "Cabernet",
        "Merlot",
        "Malbec",
        "Tempranillo",
        "Syrah",
        "Sauvignon Blanc",
        "Chardonnay",
        "Pinot Noir",
        "Cava",
    ]
    return f"{DEMO_WINE_PREFIX} {index + 1:02d} {regions[index % len(regions)]} {grapes[index % len(grapes)]}"


def _ensure_demo_stores(session: Session) -> list[Store]:
    seeds = [
        ("Demo Store Mercado Centro", "supermarket", "https://demo.local/mercado-centro"),
        ("Demo Store Vinos Selectos", "specialty", "https://demo.local/vinos-selectos"),
        ("Demo Store Bodega Norte", "specialty", "https://demo.local/bodega-norte"),
        ("Demo Store Ahorra Max", "supermarket", "https://demo.local/ahorra-max"),
    ]
    stores: list[Store] = []
    for name, category, base_url in seeds:
        row = session.execute(select(Store).where(Store.name == name)).scalar_one_or_none()
        if row is None:
            row = Store(name=name, category=category, base_url=base_url, enabled=True)
            session.add(row)
            session.flush()
        else:
            row.enabled = True
            row.category = category
            row.base_url = base_url
        stores.append(row)
    session.commit()
    return stores


def _reset_demo_data(session: Session) -> None:
    wine_ids = [
        row[0]
        for row in session.execute(
            select(Wine.id).where(Wine.canonical_name.like(f"{DEMO_WINE_PREFIX}%"))
        ).all()
    ]
    store_ids = [
        row[0]
        for row in session.execute(
            select(Store.id).where(Store.name.like(f"{DEMO_STORE_PREFIX}%"))
        ).all()
    ]

    if wine_ids:
        session.execute(delete(UserRating).where(UserRating.wine_id.in_(wine_ids)))
        session.execute(delete(ReviewAggregate).where(ReviewAggregate.wine_id.in_(wine_ids)))
        session.execute(delete(ExternalReview).where(ExternalReview.wine_id.in_(wine_ids)))
        session.execute(delete(PriceHistory).where(PriceHistory.wine_id.in_(wine_ids)))
        session.execute(delete(Offer).where(Offer.wine_id.in_(wine_ids)))
        session.execute(delete(Wine).where(Wine.id.in_(wine_ids)))
    if store_ids:
        session.execute(delete(Offer).where(Offer.store_id.in_(store_ids)))
        session.execute(delete(Store).where(Store.id.in_(store_ids)))

    # Keep only the latest recommendation run after we reseed.
    session.execute(delete(Recommendation))
    session.execute(delete(RecommendationRun))
    session.commit()


def _wine_type(index: int) -> str:
    return ["red", "white", "rose", "sparkling", "other"][index % 5]


def _sweetness(index: int) -> str:
    if index % 13 == 0:
        return "sweet"
    if index % 7 == 0:
        return "off-dry"
    return "dry"


def _grapes_by_type(wine_type: str) -> list[str]:
    mapping = {
        "red": ["cabernet sauvignon", "merlot"],
        "white": ["sauvignon blanc", "chardonnay"],
        "rose": ["grenache", "syrah"],
        "sparkling": ["macabeo", "xarel-lo"],
        "other": ["tempranillo"],
    }
    return mapping.get(wine_type, ["tempranillo"])


def seed_demo_data(
    session: Session,
    total_wines: int = 45,
    *,
    reset: bool = True,
    run_pipeline_after_seed: bool = True,
) -> DemoSeedSummary:
    if total_wines < 1:
        raise ValueError("total_wines must be positive.")
    if total_wines > 250:
        raise ValueError("total_wines too large for lightweight demo seed.")

    if reset:
        _reset_demo_data(session)
    stores = _ensure_demo_stores(session)
    now = datetime.utcnow()

    ratings_a = 0
    ratings_b = 0

    for idx in range(total_wines):
        canonical_name = _demo_wine_name(idx)
        wine = session.execute(select(Wine).where(Wine.canonical_name == canonical_name)).scalar_one_or_none()
        wine_type = _wine_type(idx)
        if wine is None:
            wine = Wine(
                canonical_name=canonical_name,
                producer=f"Demo Producer {idx % 10 + 1}",
                country="Mexico",
                region="Jalisco",
                type=wine_type,
                grapes=_grapes_by_type(wine_type),
                sweetness=_sweetness(idx),
                is_grape_wine=(idx % 11 != 0),
            )
            session.add(wine)
            session.flush()

        session.merge(
            ReviewAggregate(
                wine_id=wine.id,
                avg_rating=round(3.2 + (idx % 9) * 0.2, 2),
                rating_scale="5",
                descriptors={
                    "items": [
                        {"tag": "fruity" if idx % 2 == 0 else "oaky", "confidence": 0.75},
                        {"tag": "balanced", "confidence": 0.7},
                    ]
                },
                pros=["good value", "balanced acidity"],
                cons=["finish can vary"],
                disagreement_summary="Panelists differ on body and finish intensity.",
            )
        )

        for offer_offset in range(2):
            store = stores[(idx + offer_offset) % len(stores)]
            product_url = f"{store.base_url}/wine-{idx + 1:02d}-offer-{offer_offset + 1}"
            existing_offer = session.execute(select(Offer).where(Offer.product_url == product_url)).scalar_one_or_none()
            if existing_offer is not None:
                continue

            price = round(85 + (idx * 9 + offer_offset * 17) % 520, 2)
            offer = Offer(
                store_id=store.id,
                wine_id=wine.id,
                listed_name=canonical_name,
                price_mxn=price,
                discount_text="discount:-10%" if idx % 4 == 0 else None,
                volume_ml=750,
                availability="in_stock" if idx % 10 != 0 else "unknown",
                product_url=product_url,
                captured_at=now - timedelta(days=(idx + offer_offset) % 21),
                match_confidence=0.95,
            )
            session.add(offer)
            session.flush()
            session.add(
                PriceHistory(
                    wine_id=wine.id,
                    store_id=store.id,
                    price_mxn=price,
                    captured_at=offer.captured_at,
                )
            )

        # A rates around half; includes favorites.
        if idx % 2 == 0:
            existing_a = session.execute(
                select(UserRating).where(UserRating.user_id == "A", UserRating.wine_id == wine.id)
            ).scalar_one_or_none()
            if existing_a is None:
                session.add(
                    UserRating(
                        user_id="A",
                        wine_id=wine.id,
                        rating_1_5=[5, 4, 3, 4, 5][idx % 5],
                        comment=f"Demo A tasting note {idx + 1}",
                        tried_at=now - timedelta(days=idx % 15),
                    )
                )
                ratings_a += 1

        # B rates about one third; different profile.
        if idx % 3 == 0:
            existing_b = session.execute(
                select(UserRating).where(UserRating.user_id == "B", UserRating.wine_id == wine.id)
            ).scalar_one_or_none()
            if existing_b is None:
                session.add(
                    UserRating(
                        user_id="B",
                        wine_id=wine.id,
                        rating_1_5=[2, 3, 4, 5][idx % 4],
                        comment=f"Demo B tasting note {idx + 1}",
                        tried_at=now - timedelta(days=idx % 18),
                    )
                )
                ratings_b += 1

    session.commit()

    run_id: str | None = None
    if run_pipeline_after_seed:
        run_result = run_pipeline(session, mode="manual")
        run_id = run_result.run_id

    demo_wines = (
        session.execute(select(Wine).where(Wine.canonical_name.like(f"{DEMO_WINE_PREFIX}%")))
        .scalars()
        .all()
    )
    demo_offers = (
        session.execute(
            select(Offer)
            .join(Wine, Wine.id == Offer.wine_id)
            .where(Wine.canonical_name.like(f"{DEMO_WINE_PREFIX}%"))
        )
        .scalars()
        .all()
    )
    return DemoSeedSummary(
        demo_wines=len(demo_wines),
        demo_offers=len(demo_offers),
        ratings_a=ratings_a,
        ratings_b=ratings_b,
        run_id=run_id,
    )

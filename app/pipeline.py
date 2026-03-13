from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from sqlalchemy import Select, delete, func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.llm_client import LLMClient, build_llm_client_from_settings
from app.matching import match_listed_wine
from app.models import (
    ExternalReview,
    Offer,
    PriceHistory,
    RawPage,
    Recommendation,
    RecommendationRun,
    ReviewAggregate,
    Store,
    User,
    UserRating,
    Wine,
)
from app.schema_validation import load_schema, validate_json
from app.scoring import ScoringInput, build_explanation, score_offer
from app.time_utils import utc_now_compact, utc_now_naive


@dataclass(slots=True)
class PipelineResult:
    run_id: str
    status: str
    summary_path: str


def _ensure_dirs(run_id: str) -> tuple[Path, Path]:
    run_dir = settings.artifacts_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = settings.artifacts_root / "raw_pages" / utc_now_naive().strftime("%Y-%m")
    raw_dir.mkdir(parents=True, exist_ok=True)
    return run_dir, raw_dir


def _seed_stores(session: Session) -> None:
    if session.execute(select(func.count(Store.id))).scalar_one() > 0:
        return
    seeds = [
        Store(
            name="La Playa",
            category="specialty",
            base_url="https://example.com/la-playa",
            enabled=True,
        ),
        Store(
            name="Vinos Americas",
            category="specialty",
            base_url="https://example.com/vinos-americas",
            enabled=True,
        ),
        Store(
            name="Supermarket MX",
            category="supermarket",
            base_url="https://example.com/supermarket-mx",
            enabled=True,
        ),
    ]
    session.add_all(seeds)
    session.commit()


def _discover_sources(session: Session) -> dict[int, list[str]]:
    sources: dict[int, list[str]] = {}
    rows = session.execute(select(Store).where(Store.enabled.is_(True))).scalars().all()
    for row in rows:
        sources[row.id] = [f"{row.base_url}/catalog"]
    return sources


def _mock_page_payload(store_name: str, url: str) -> str:
    catalog = {
        "La Playa": [
            "Casillero del Diablo Cabernet Sauvignon | 199 | discount:-10% | 750 | in_stock | https://example.com/p/casillero-cab",
            "JP Chenet Merlot | 159 | none | 750 | in_stock | https://example.com/p/jp-chenet-merlot",
        ],
        "Vinos Americas": [
            "Trapiche Malbec Reserve | 239 | none | 750 | in_stock | https://example.com/p/trapiche-malbec",
            "Freixenet Cordon Negro Brut | 299 | discount:-15% | 750 | in_stock | https://example.com/p/freixenet-negro",
        ],
        "Supermarket MX": [
            "Santa Carolina Cabernet Sauvignon | 129 | none | 750 | in_stock | https://example.com/p/santa-carolina",
            "Yellow Tail Shiraz | 219 | none | 750 | in_stock | https://example.com/p/yellow-tail-shiraz",
        ],
    }
    lines = catalog.get(store_name, [])
    return "\n".join(lines) + f"\n# source:{url}"


def _fetch_and_store_pages(
    session: Session,
    sources: dict[int, list[str]],
    raw_dir: Path,
) -> list[RawPage]:
    captured: list[RawPage] = []
    for store_id, urls in sources.items():
        store = session.get(Store, store_id)
        if store is None:
            continue
        for url in urls[: settings.max_pages_per_store]:
            text = _mock_page_payload(store.name, url)
            content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            file_path = raw_dir / f"{content_hash}.html"
            file_path.write_text(text, encoding="utf-8")

            existing = session.execute(
                select(RawPage).where(RawPage.url == url, RawPage.content_hash == content_hash)
            ).scalar_one_or_none()
            if existing is not None:
                captured.append(existing)
                continue

            row = RawPage(
                store_id=store_id,
                url=url,
                content_ref=str(file_path),
                content_hash=content_hash,
                fetch_status="success",
            )
            session.add(row)
            captured.append(row)
    session.commit()
    return captured


def _extract_and_store_offers(session: Session, llm: LLMClient, pages: list[RawPage]) -> int:
    offers_schema = load_schema("schemas/offers.schema.json")
    created = 0
    llm_calls = 0

    for page in pages:
        if llm_calls >= settings.max_llm_calls_per_run:
            break
        text = Path(page.content_ref).read_text(encoding="utf-8")
        extracted = llm.extract_offers(text, offers_schema)
        validate_json(extracted, offers_schema)
        llm_calls += 1

        candidate_wines = session.execute(select(Wine.id, Wine.canonical_name)).all()
        for item in extracted.get("offers", []):
            listed_name = str(item["product_name"])
            match = match_listed_wine(listed_name, [(w[0], w[1]) for w in candidate_wines])
            wine_id = match.wine_id
            if wine_id is None and match.confidence < 0.6:
                canonical = listed_name.strip()
                wine = session.execute(select(Wine).where(Wine.canonical_name == canonical)).scalar_one_or_none()
                if wine is None:
                    wine = Wine(
                        canonical_name=canonical,
                        type="red" if "cabernet" in listed_name.lower() or "merlot" in listed_name.lower() else None,
                        sweetness="dry",
                        is_grape_wine=True,
                    )
                    session.add(wine)
                    session.flush()
                wine_id = wine.id

            offer = Offer(
                store_id=page.store_id,
                wine_id=wine_id,
                listed_name=listed_name,
                price_mxn=float(item["price_mxn"]),
                discount_text=item.get("discount_text"),
                volume_ml=item.get("volume_ml"),
                availability=str(item.get("availability", "unknown")),
                product_url=str(item.get("url", "")),
                match_confidence=float(item.get("confidence", 0.0)),
            )
            session.add(offer)
            session.flush()
            if wine_id is not None:
                session.add(
                    PriceHistory(
                        wine_id=wine_id,
                        store_id=page.store_id,
                        price_mxn=float(item["price_mxn"]),
                    )
                )
            created += 1
    session.commit()
    return created


def _enrich_reviews(session: Session, llm: LLMClient) -> int:
    review_schema = load_schema("schemas/review_summary.schema.json")
    created = 0
    wines = session.execute(select(Wine)).scalars().all()

    for wine in wines:
        existing = session.get(ReviewAggregate, wine.id)
        if existing is not None:
            continue
        search_results = llm.search(f"{wine.canonical_name} wine review")
        texts = [r.snippet for r in search_results]
        summary = llm.summarize_reviews(texts)
        validate_json(summary, review_schema)

        review = ExternalReview(
            wine_id=wine.id,
            source_name=search_results[0].title if search_results else "unknown",
            source_url=search_results[0].url if search_results else "https://example.com",
            raw_ref="inline",
            extracted_json=summary,
        )
        session.add(review)
        session.merge(
            ReviewAggregate(
                wine_id=wine.id,
                avg_rating=summary.get("avg_rating"),
                rating_scale=str(summary.get("rating_scale")) if summary.get("rating_scale") else None,
                descriptors={"items": summary.get("descriptors", [])},
                pros=summary.get("pros", []),
                cons=summary.get("cons", []),
                disagreement_summary=summary.get("disagreement_summary"),
            )
        )
        created += 1
    session.commit()
    return created


def _user_liked_wines(session: Session, user_id: str, threshold: int = 4) -> set[int]:
    rows = session.execute(
        select(UserRating.wine_id).where(UserRating.user_id == user_id, UserRating.rating_1_5 >= threshold)
    ).all()
    return {row[0] for row in rows}


def _user_tried_wines(session: Session, user_id: str) -> set[int]:
    rows = session.execute(select(UserRating.wine_id).where(UserRating.user_id == user_id)).all()
    return {row[0] for row in rows}


def _descriptor_match(session: Session, wine_id: int, user_id: str) -> float:
    liked = _user_liked_wines(session, user_id)
    if not liked:
        return 0.65
    current = session.get(ReviewAggregate, wine_id)
    if current is None:
        return 0.5
    tags = {d.get("tag") for d in (current.descriptors or {}).get("items", []) if isinstance(d, dict)}
    if not tags:
        return 0.55

    liked_tags: set[str] = set()
    for liked_wine_id in liked:
        agg = session.get(ReviewAggregate, liked_wine_id)
        if agg is None:
            continue
        liked_tags |= {
            d.get("tag") for d in (agg.descriptors or {}).get("items", []) if isinstance(d, dict) and d.get("tag")
        }
    if not liked_tags:
        return 0.6
    overlap = len(tags & liked_tags) / max(len(tags | liked_tags), 1)
    return max(0.2, min(overlap, 1.0))


def _latest_offer_per_wine(session: Session) -> dict[int, Offer]:
    rows = session.execute(select(Offer).order_by(Offer.captured_at.desc())).scalars().all()
    latest: dict[int, Offer] = {}
    for row in rows:
        if row.wine_id is None:
            continue
        if row.wine_id not in latest:
            latest[row.wine_id] = row
    return latest


def _cheapest_offer_per_wine(session: Session) -> dict[int, Offer]:
    rows = session.execute(select(Offer).order_by(Offer.price_mxn.asc())).scalars().all()
    cheapest: dict[int, Offer] = {}
    for row in rows:
        if row.wine_id is None:
            continue
        if row.wine_id not in cheapest:
            cheapest[row.wine_id] = row
    return cheapest


def _write_recommendations(session: Session, run_id: str) -> int:
    created = 0
    latest = _latest_offer_per_wine(session)
    cheapest = _cheapest_offer_per_wine(session)
    users = session.execute(select(User)).scalars().all()
    session.execute(delete(Recommendation).where(Recommendation.run_id == run_id))

    for user in users:
        tried = _user_tried_wines(session, user.id)
        liked = _user_liked_wines(session, user.id, threshold=4)

        recs: list[tuple[int, Offer, float, str]] = []
        for wine_id, offer in latest.items():
            if wine_id in tried:
                continue
            wine = session.get(Wine, wine_id)
            agg = session.get(ReviewAggregate, wine_id)
            if wine is None:
                continue
            d_match = _descriptor_match(session, wine_id, user.id)
            sc = score_offer(
                ScoringInput(
                    price_mxn=float(offer.price_mxn),
                    discount_text=offer.discount_text,
                    external_rating=agg.avg_rating if agg else None,
                    descriptor_match=d_match,
                    wow_deal=float(offer.price_mxn) < 130,
                    sweetness=wine.sweetness,
                    is_grape_wine=wine.is_grape_wine,
                )
            )
            if sc < 0:
                continue
            reason = build_explanation(
                locale=user.locale,
                descriptor_match=d_match,
                price_mxn=float(offer.price_mxn),
                external_rating=agg.avg_rating if agg else None,
                conflict_note=agg.disagreement_summary if agg else None,
            )
            recs.append((wine_id, offer, sc, reason))

        recs.sort(key=lambda x: x[2], reverse=True)
        for rank, (wine_id, offer, sc, reason) in enumerate(recs[:10], start=1):
            session.add(
                Recommendation(
                    run_id=run_id,
                    user_id=user.id,
                    kind="recommended_buys",
                    rank=rank,
                    wine_id=wine_id,
                    offer_id=offer.id,
                    score=sc,
                    explanation=reason,
                    explanation_locale=user.locale,
                )
            )
            created += 1

        favorites: list[tuple[int, Offer, float, str]] = []
        for wine_id in liked:
            offer = cheapest.get(wine_id)
            if offer is None:
                continue
            wine = session.get(Wine, wine_id)
            agg = session.get(ReviewAggregate, wine_id)
            if wine is None:
                continue
            d_match = _descriptor_match(session, wine_id, user.id)
            sc = score_offer(
                ScoringInput(
                    price_mxn=float(offer.price_mxn),
                    discount_text=offer.discount_text,
                    external_rating=agg.avg_rating if agg else None,
                    descriptor_match=d_match,
                    wow_deal=float(offer.price_mxn) < 130,
                    sweetness=wine.sweetness,
                    is_grape_wine=wine.is_grape_wine,
                )
            )
            reason = build_explanation(
                locale=user.locale,
                descriptor_match=d_match,
                price_mxn=float(offer.price_mxn),
                external_rating=agg.avg_rating if agg else None,
                conflict_note=agg.disagreement_summary if agg else None,
            )
            favorites.append((wine_id, offer, sc, reason))

        favorites.sort(key=lambda x: float(x[1].price_mxn))
        for rank, (wine_id, offer, sc, reason) in enumerate(favorites[:10], start=1):
            session.add(
                Recommendation(
                    run_id=run_id,
                    user_id=user.id,
                    kind="cheapest_favorites",
                    rank=rank,
                    wine_id=wine_id,
                    offer_id=offer.id,
                    score=sc,
                    explanation=reason,
                    explanation_locale=user.locale,
                )
            )
            created += 1
    session.commit()
    return created


def run_pipeline(session: Session, mode: str, llm: LLMClient | None = None) -> PipelineResult:
    llm = llm or build_llm_client_from_settings()
    run_id = utc_now_compact() + "-" + uuid.uuid4().hex[:8]
    run_dir, raw_dir = _ensure_dirs(run_id)
    started_at = utc_now_naive()
    run = RecommendationRun(
        id=run_id,
        mode=mode,
        started_at=started_at,
        status="fail",
        logs_ref=str(run_dir / "run_summary.json"),
    )
    session.add(run)
    session.commit()

    summary: dict[str, object] = {
        "run_id": run_id,
        "mode": mode,
        "started_at": started_at.isoformat(),
        "steps": {},
        "counts": {},
        "status": "fail",
    }

    try:
        t0 = perf_counter()
        _seed_stores(session)
        sources = _discover_sources(session)
        summary["steps"]["discover_sources_seconds"] = round(perf_counter() - t0, 3)
        summary["counts"]["stores"] = len(sources)

        t1 = perf_counter()
        pages = _fetch_and_store_pages(session, sources, raw_dir)
        summary["steps"]["fetch_pages_seconds"] = round(perf_counter() - t1, 3)
        summary["counts"]["pages_fetched"] = len(pages)

        t2 = perf_counter()
        offers_count = _extract_and_store_offers(session, llm, pages)
        summary["steps"]["extract_offers_seconds"] = round(perf_counter() - t2, 3)
        summary["counts"]["offers_extracted"] = offers_count

        t3 = perf_counter()
        reviews_count = _enrich_reviews(session, llm)
        summary["steps"]["enrich_reviews_seconds"] = round(perf_counter() - t3, 3)
        summary["counts"]["review_aggregates_created"] = reviews_count

        t4 = perf_counter()
        recommendations_count = _write_recommendations(session, run_id)
        summary["steps"]["score_rank_write_seconds"] = round(perf_counter() - t4, 3)
        summary["counts"]["recommendations_created"] = recommendations_count

        summary["status"] = "success"
        run.status = "success"
    except Exception:  # noqa: BLE001
        run.status = "fail"
        raise
    finally:
        run.finished_at = utc_now_naive()
        summary["finished_at"] = run.finished_at.isoformat()
        summary_path = Path(run.logs_ref)
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        session.add(run)
        session.commit()

    return PipelineResult(run_id=run_id, status=run.status, summary_path=run.logs_ref)


def latest_run_query(success_only: bool = True) -> Select[tuple[RecommendationRun]]:
    query = select(RecommendationRun)
    if success_only:
        query = query.where(RecommendationRun.status == "success")
    return query.order_by(RecommendationRun.started_at.desc())

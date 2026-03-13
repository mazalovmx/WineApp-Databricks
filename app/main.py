from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.auth import AuthUser, authenticate_user, ensure_default_users, get_current_user, make_token
from app.config import settings
from app.db import Base, engine, get_session
from app.models import Offer, Recommendation, RecommendationRun, ReviewAggregate, User, UserRating, Wine
from app.pipeline import latest_run_query, run_pipeline
from app.schemas import (
    HealthResponse,
    LoginRequest,
    LoginResponse,
    RatingCreateRequest,
    RecommendationsResponse,
    RecommendationItem,
    TriedWineItem,
    TriggerRunRequest,
    UserMeResponse,
)


app = FastAPI(title="Guadalajara Wine Finder", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    Path("data").mkdir(parents=True, exist_ok=True)
    settings.artifacts_root.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        ensure_default_users(session)


@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    return FileResponse("app/static/index.html")


app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/health", response_model=HealthResponse)
def health(session: Session = Depends(get_session)) -> HealthResponse:
    run = session.execute(latest_run_query(success_only=True)).scalars().first()
    if run is None:
        return HealthResponse(status="ok", last_successful_run=None, data_freshness="no_successful_runs_yet")
    freshness = "fresh" if (datetime.utcnow() - run.finished_at).total_seconds() < 60 * 60 * 30 else "stale"
    return HealthResponse(status="ok", last_successful_run=run.finished_at, data_freshness=freshness)


@app.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest, session: Session = Depends(get_session)) -> LoginResponse:
    if not authenticate_user(session, payload.user_id, payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    return LoginResponse(access_token=make_token(payload.user_id))


@app.get("/users/me", response_model=UserMeResponse)
def me(
    current_user: Annotated[AuthUser, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> UserMeResponse:
    user = session.get(User, current_user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return UserMeResponse(id=user.id, display_name=user.display_name, locale=user.locale)


@app.get("/recommendations", response_model=RecommendationsResponse)
def recommendations(
    kind: Annotated[str, Query(pattern="^(recommended_buys|cheapest_favorites)$")],
    date: str | None = None,  # retained for API compatibility
    current_user: Annotated[AuthUser, Depends(get_current_user)] = None,
    session: Session = Depends(get_session),
) -> RecommendationsResponse:
    _ = date
    run = session.execute(latest_run_query(success_only=True)).scalars().first()
    if run is None:
        raise HTTPException(status_code=404, detail="No successful recommendation run found.")
    rows = (
        session.execute(
            select(Recommendation)
            .where(
                and_(
                    Recommendation.run_id == run.id,
                    Recommendation.user_id == current_user.id,
                    Recommendation.kind == kind,
                )
            )
            .order_by(Recommendation.rank.asc())
        )
        .scalars()
        .all()
    )
    return RecommendationsResponse(
        run_id=run.id,
        kind=kind,
        items=[
            RecommendationItem(
                rank=row.rank,
                wine_id=row.wine_id,
                offer_id=row.offer_id,
                score=row.score,
                explanation=row.explanation,
                explanation_locale=row.explanation_locale,
            )
            for row in rows
        ],
    )


@app.get("/favorites/cheapest", response_model=RecommendationsResponse)
def favorites_cheapest(
    current_user: Annotated[AuthUser, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> RecommendationsResponse:
    return recommendations("cheapest_favorites", None, current_user, session)


@app.get("/wines/tried", response_model=list[TriedWineItem])
def tried_wines(
    query: str | None = None,
    wine_type: str | None = None,
    grape: str | None = None,
    current_user: Annotated[AuthUser, Depends(get_current_user)] = None,
    session: Session = Depends(get_session),
) -> list[TriedWineItem]:
    base = (
        select(Wine, UserRating)
        .join(UserRating, UserRating.wine_id == Wine.id)
        .where(UserRating.user_id == current_user.id)
        .order_by(UserRating.tried_at.desc())
    )
    filters = []
    if query:
        filters.append(func.lower(Wine.canonical_name).contains(query.lower()))
    if wine_type:
        filters.append(Wine.type == wine_type)
    if grape:
        filters.append(func.lower(func.cast(Wine.grapes, str)).contains(grape.lower()))
    if filters:
        base = base.where(and_(*filters))
    rows = session.execute(base).all()

    grouped: dict[int, TriedWineItem] = {}
    for wine, rating in rows:
        if wine.id not in grouped:
            latest_offer = (
                session.execute(
                    select(Offer).where(Offer.wine_id == wine.id).order_by(Offer.captured_at.desc()).limit(1)
                )
                .scalars()
                .first()
            )
            grouped[wine.id] = TriedWineItem(
                wine_id=wine.id,
                canonical_name=wine.canonical_name,
                ratings=[],
                last_known_offer_price=float(latest_offer.price_mxn) if latest_offer else None,
            )
        grouped[wine.id].ratings.append(
            {
                "rating_1_5": rating.rating_1_5,
                "comment": rating.comment,
                "tried_at": rating.tried_at.isoformat(),
            }
        )
    return list(grouped.values())


@app.post("/ratings")
def add_rating(
    payload: RatingCreateRequest,
    current_user: Annotated[AuthUser, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> dict[str, object]:
    wine = session.get(Wine, payload.wine_id)
    if wine is None:
        raise HTTPException(status_code=404, detail="Wine not found.")
    row = UserRating(
        user_id=current_user.id,
        wine_id=payload.wine_id,
        rating_1_5=payload.rating_1_5,
        comment=payload.comment,
        tried_at=payload.tried_at or datetime.utcnow(),
    )
    session.add(row)
    session.commit()
    return {"ok": True, "rating_id": row.id}


@app.post("/runs/trigger")
def trigger_run(
    payload: TriggerRunRequest,
    current_user: Annotated[AuthUser, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> dict[str, str]:
    if current_user.id != "A":
        raise HTTPException(status_code=403, detail="Only user A can trigger runs.")
    result = run_pipeline(session, mode=payload.mode)
    return {"run_id": result.run_id, "status": result.status}


@app.get("/status/last-run")
def status_last_run(session: Session = Depends(get_session)) -> dict[str, object]:
    run = session.execute(select(RecommendationRun).order_by(RecommendationRun.started_at.desc())).scalars().first()
    if run is None:
        return {"run": None}
    stale_stores = session.execute(
        select(func.count(Offer.id)).where(or_(Offer.availability == "unknown", Offer.availability == "out_of_stock"))
    ).scalar_one()
    return {
        "run_id": run.id,
        "status": run.status,
        "started_at": run.started_at,
        "finished_at": run.finished_at,
        "logs_ref": run.logs_ref,
        "stale_offer_count": stale_stores,
    }

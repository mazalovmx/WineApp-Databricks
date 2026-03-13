from __future__ import annotations

from datetime import date

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import services
from app.config import STATIC_DIR, TEMPLATES_DIR
from app.database import get_deals, insert_deals
from app.models import WineDeal

app = FastAPI(title="WineApp", version="1.0.0")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, deal_date: str | None = Query(default=None)):
    target = date.fromisoformat(deal_date) if deal_date else date.today()
    deals = await get_deals(deal_date=str(target))

    if not deals:
        fresh = await services.fetch_deals(target_date=target)
        await insert_deals(fresh)
        deals = fresh

    summary = services.summarize(deals, target_date=target)
    return templates.TemplateResponse(
        request,
        "index.html",
        {"deals": deals, "summary": summary, "deal_date": str(target)},
    )


@app.get("/api/deals", response_model=list[WineDeal])
async def api_deals(deal_date: str | None = Query(default=None)):
    target = date.fromisoformat(deal_date) if deal_date else date.today()
    deals = await get_deals(deal_date=str(target))

    if not deals:
        fresh = await services.fetch_deals(target_date=target)
        await insert_deals(fresh)
        deals = fresh

    return deals


@app.get("/api/refresh", response_model=list[WineDeal])
async def api_refresh(deal_date: str | None = Query(default=None)):
    target = date.fromisoformat(deal_date) if deal_date else date.today()
    fresh = await services.fetch_deals(target_date=target)
    await insert_deals(fresh)
    return fresh


@app.get("/health")
async def health():
    return {"status": "ok"}

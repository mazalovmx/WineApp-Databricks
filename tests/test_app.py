from datetime import date

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models import DealSummary, WineDeal
from app.services import fetch_deals, summarize


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

def test_wine_deal_discount_calculation():
    deal = WineDeal(name="Test Wine", original_price=100.0, deal_price=75.0)
    assert deal.discount_pct == 25.0


def test_wine_deal_zero_original_price():
    deal = WineDeal(name="Free Wine", original_price=0.0, deal_price=0.0)
    assert deal.discount_pct == 0.0


# ---------------------------------------------------------------------------
# Service tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_fetch_deals_returns_list():
    deals = await fetch_deals(target_date=date(2026, 1, 15))
    assert isinstance(deals, list)
    assert len(deals) > 0
    assert all(isinstance(d, WineDeal) for d in deals)


@pytest.mark.asyncio
async def test_fetch_deals_deterministic():
    a = await fetch_deals(target_date=date(2026, 3, 1))
    b = await fetch_deals(target_date=date(2026, 3, 1))
    assert [d.name for d in a] == [d.name for d in b]


def test_summarize_empty():
    summary = summarize([], target_date=date(2026, 1, 1))
    assert summary.total_deals == 0
    assert summary.best_deal is None


def test_summarize_with_deals():
    deals = [
        WineDeal(name="A", original_price=50, deal_price=30),
        WineDeal(name="B", original_price=100, deal_price=60),
    ]
    summary = summarize(deals)
    assert summary.total_deals == 2
    assert summary.avg_discount > 0
    assert summary.best_deal is not None


# ---------------------------------------------------------------------------
# API tests
# ---------------------------------------------------------------------------

@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_api_deals_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/deals", params={"deal_date": "2026-02-01"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_home_returns_html():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/", params={"deal_date": "2026-02-01"})
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "WineApp" in resp.text

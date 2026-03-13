"""Wine deal generation and aggregation logic.

In a production app this module would scrape retailer sites or call
third-party APIs.  For now it generates realistic sample deals so the
app is fully functional out of the box.
"""

from __future__ import annotations

import random
from datetime import date

from app.models import DealSummary, WineDeal

_WINES: list[dict] = [
    {"name": "Château Margaux 2018", "region": "Bordeaux", "grape": "Cabernet Sauvignon"},
    {"name": "Cloudy Bay Sauvignon Blanc 2023", "region": "Marlborough", "grape": "Sauvignon Blanc"},
    {"name": "Penfolds Bin 389 2020", "region": "South Australia", "grape": "Cabernet Shiraz"},
    {"name": "Whispering Angel Rosé 2023", "region": "Provence", "grape": "Grenache"},
    {"name": "Kim Crawford Sauvignon Blanc 2023", "region": "Marlborough", "grape": "Sauvignon Blanc"},
    {"name": "Meiomi Pinot Noir 2022", "region": "California", "grape": "Pinot Noir"},
    {"name": "Oyster Bay Chardonnay 2022", "region": "Marlborough", "grape": "Chardonnay"},
    {"name": "Josh Cellars Cabernet Sauvignon 2021", "region": "California", "grape": "Cabernet Sauvignon"},
    {"name": "La Crema Sonoma Coast Pinot Noir 2021", "region": "Sonoma", "grape": "Pinot Noir"},
    {"name": "Decoy by Duckhorn Merlot 2021", "region": "Sonoma", "grape": "Merlot"},
    {"name": "Apothic Red Blend 2022", "region": "California", "grape": "Red Blend"},
    {"name": "Bread & Butter Chardonnay 2022", "region": "California", "grape": "Chardonnay"},
    {"name": "Santa Margherita Pinot Grigio 2023", "region": "Alto Adige", "grape": "Pinot Grigio"},
    {"name": "Kendall-Jackson Vintner's Reserve Chardonnay 2022", "region": "California", "grape": "Chardonnay"},
    {"name": "Caymus Cabernet Sauvignon 2021", "region": "Napa Valley", "grape": "Cabernet Sauvignon"},
    {"name": "Silver Oak Alexander Valley 2019", "region": "Sonoma", "grape": "Cabernet Sauvignon"},
    {"name": "Ruffino Chianti Classico 2021", "region": "Tuscany", "grape": "Sangiovese"},
    {"name": "Campo Viejo Tempranillo 2021", "region": "Rioja", "grape": "Tempranillo"},
    {"name": "Dr. Loosen Blue Slate Riesling 2022", "region": "Mosel", "grape": "Riesling"},
    {"name": "Minuty M Rosé 2023", "region": "Provence", "grape": "Grenache"},
]

_SOURCES = ["WineSearcher", "Vivino", "TotalWine", "Wine.com", "Drizly"]


def _generate_sample_deals(count: int = 10, target_date: date | None = None) -> list[WineDeal]:
    target_date = target_date or date.today()
    rng = random.Random(str(target_date))
    selected = rng.sample(_WINES, min(count, len(_WINES)))
    deals: list[WineDeal] = []
    for wine in selected:
        original = round(rng.uniform(12.0, 120.0), 2)
        discount = rng.uniform(0.10, 0.45)
        deal_price = round(original * (1 - discount), 2)
        deals.append(
            WineDeal(
                name=wine["name"],
                region=wine["region"],
                grape=wine["grape"],
                original_price=original,
                deal_price=deal_price,
                source=rng.choice(_SOURCES),
                deal_date=target_date,
            )
        )
    deals.sort(key=lambda d: d.discount_pct, reverse=True)
    return deals


async def fetch_deals(target_date: date | None = None) -> list[WineDeal]:
    return _generate_sample_deals(target_date=target_date)


def summarize(deals: list[WineDeal], target_date: date | None = None) -> DealSummary:
    if not deals:
        return DealSummary(deal_date=target_date or date.today())
    avg_disc = round(sum(d.discount_pct for d in deals) / len(deals), 1)
    best = max(deals, key=lambda d: d.discount_pct)
    return DealSummary(
        total_deals=len(deals),
        avg_discount=avg_disc,
        best_deal=best,
        deal_date=target_date or date.today(),
    )

from __future__ import annotations

import aiosqlite

from app.config import DATABASE_PATH
from app.models import WineDeal

_SCHEMA = """
CREATE TABLE IF NOT EXISTS deals (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    region      TEXT    DEFAULT '',
    grape       TEXT    DEFAULT '',
    original_price REAL NOT NULL,
    deal_price     REAL NOT NULL,
    discount_pct   REAL DEFAULT 0,
    source      TEXT    DEFAULT '',
    url         TEXT    DEFAULT '',
    image_url   TEXT    DEFAULT '',
    deal_date   TEXT    NOT NULL,
    created_at  TEXT    DEFAULT (datetime('now'))
);
"""


async def _get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(str(DATABASE_PATH))
    db.row_factory = aiosqlite.Row
    await db.execute(_SCHEMA)
    await db.commit()
    return db


async def insert_deals(deals: list[WineDeal]) -> int:
    db = await _get_db()
    try:
        count = 0
        for deal in deals:
            await db.execute(
                """INSERT INTO deals
                   (name, region, grape, original_price, deal_price,
                    discount_pct, source, url, image_url, deal_date)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    deal.name,
                    deal.region,
                    deal.grape,
                    deal.original_price,
                    deal.deal_price,
                    deal.discount_pct,
                    deal.source,
                    deal.url,
                    deal.image_url,
                    str(deal.deal_date),
                ),
            )
            count += 1
        await db.commit()
        return count
    finally:
        await db.close()


async def get_deals(deal_date: str | None = None, limit: int = 50) -> list[WineDeal]:
    db = await _get_db()
    try:
        if deal_date:
            cursor = await db.execute(
                "SELECT * FROM deals WHERE deal_date = ? ORDER BY discount_pct DESC LIMIT ?",
                (deal_date, limit),
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM deals ORDER BY deal_date DESC, discount_pct DESC LIMIT ?",
                (limit,),
            )
        rows = await cursor.fetchall()
        return [WineDeal(**dict(row)) for row in rows]
    finally:
        await db.close()


async def get_deal_dates() -> list[str]:
    db = await _get_db()
    try:
        cursor = await db.execute(
            "SELECT DISTINCT deal_date FROM deals ORDER BY deal_date DESC LIMIT 30"
        )
        rows = await cursor.fetchall()
        return [row["deal_date"] for row in rows]
    finally:
        await db.close()

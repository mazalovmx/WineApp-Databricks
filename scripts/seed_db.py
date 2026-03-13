#!/usr/bin/env python3
"""Seed database with users A and B."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text
from pipeline.db import get_session, init_db


def seed():
    init_db()
    with get_session() as session:
        for uid, name in [("A", "User A"), ("B", "User B")]:
            try:
                session.execute(
                    text("""
                        INSERT INTO users (id, display_name, locale)
                        VALUES (:id, :name, 'en')
                        ON CONFLICT (id) DO UPDATE SET display_name = :name
                    """),
                    {"id": uid, "name": name},
                )
            except Exception:
                # PostgreSQL: ON CONFLICT requires unique constraint; if none, just insert
                existing = session.execute(text("SELECT 1 FROM users WHERE id = :id"), {"id": uid}).fetchone()
                if not existing:
                    session.execute(
                        text("INSERT INTO users (id, display_name, locale) VALUES (:id, :name, 'en')"),
                        {"id": uid, "name": name},
                    )
        session.commit()
    print("Seeded users A and B")


if __name__ == "__main__":
    seed()

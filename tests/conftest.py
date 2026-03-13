from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from app.auth import ensure_default_users
from app.db import Base, engine


@pytest.fixture(autouse=True)
def reset_db() -> None:
    Path("data").mkdir(parents=True, exist_ok=True)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        ensure_default_users(session)
    yield

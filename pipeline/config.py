"""Pipeline configuration."""
from __future__ import annotations

import os
from datetime import datetime, timezone


def env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


DATABASE_URL = env("DATABASE_URL", "postgresql://localhost/wine_finder")
STORAGE_ROOT = env("STORAGE_ROOT", "./data")
RUN_MODE = env("RUN_MODE", "daily")  # daily, weekly, manual
MAX_PAGES_PER_STORE = int(env("MAX_PAGES_PER_STORE", "20"))
MAX_LLM_CALLS_PER_RUN = int(env("MAX_LLM_CALLS_PER_RUN", "50"))


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
    app_secret: str = os.getenv("APP_SECRET", "dev-secret-change-me")
    user_a_password: str = os.getenv("USER_A_PASSWORD", "changeme-a")
    user_b_password: str = os.getenv("USER_B_PASSWORD", "changeme-b")
    artifacts_root: Path = Path(os.getenv("ARTIFACTS_ROOT", "artifacts"))
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    max_pages_per_store: int = int(os.getenv("MAX_PAGES_PER_STORE", "20"))
    max_llm_calls_per_run: int = int(os.getenv("MAX_LLM_CALLS_PER_RUN", "300"))


settings = Settings()

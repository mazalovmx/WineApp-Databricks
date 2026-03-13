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
    llm_search_url: str = os.getenv("LLM_SEARCH_URL", "")
    llm_extract_offers_url: str = os.getenv("LLM_EXTRACT_OFFERS_URL", "")
    llm_summarize_reviews_url: str = os.getenv("LLM_SUMMARIZE_REVIEWS_URL", "")
    llm_match_entity_url: str = os.getenv("LLM_MATCH_ENTITY_URL", "")
    llm_headers_json: str = os.getenv("LLM_HEADERS_JSON", "{}")
    llm_timeout_seconds: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
    max_pages_per_store: int = int(os.getenv("MAX_PAGES_PER_STORE", "20"))
    max_llm_calls_per_run: int = int(os.getenv("MAX_LLM_CALLS_PER_RUN", "300"))


settings = Settings()

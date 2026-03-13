"""Object storage for raw pages and artifacts."""
import os
from pathlib import Path
from datetime import datetime

# Use local filesystem for MVP
DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
RAW_PAGES_DIR = DATA_DIR / "raw_pages"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
LOGS_DIR = DATA_DIR / "logs"


def init_storage():
    RAW_PAGES_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    return {
        "raw_pages": RAW_PAGES_DIR,
        "artifacts": ARTIFACTS_DIR,
        "logs": LOGS_DIR,
    }


def save_raw_page(content: str, content_hash: str) -> str:
    """Save HTML to raw_pages/<yyyy-mm>/<hash>.html. Returns path."""
    now = datetime.utcnow()
    subdir = RAW_PAGES_DIR / now.strftime("%Y-%m")
    subdir.mkdir(parents=True, exist_ok=True)
    path = subdir / f"{content_hash}.html"
    path.write_text(content, encoding="utf-8")
    return str(path.relative_to(DATA_DIR))


def load_raw_page(rel_path: str) -> str:
    path = DATA_DIR / rel_path
    return path.read_text(encoding="utf-8")


def get_run_artifacts_dir(run_id: int) -> Path:
    d = ARTIFACTS_DIR / str(run_id)
    d.mkdir(parents=True, exist_ok=True)
    return d

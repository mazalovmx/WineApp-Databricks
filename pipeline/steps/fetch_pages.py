"""Fetch store pages and store raw content."""
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List

import httpx

MAX_PAGES_PER_STORE = 50


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def run(session, storage, stores: List[dict]) -> List[dict]:
    """
    Fetch product listing pages for each store. Store raw HTML, create RawPage records.
    Returns list of {raw_page_id, store_id, url, content_ref}.
    """
    from sqlalchemy import text
    from pipeline.storage import init_storage as _init
    pages = []
    storage_obj = storage if isinstance(storage, dict) else _init()

    for store in stores[:10]:
        url = store.get("url") or store.get("base_url")
        if not url:
            continue
        try:
            with httpx.Client(follow_redirects=True, timeout=30.0) as client:
                resp = client.get(url)
                resp.raise_for_status()
                content = resp.text
        except Exception:
            continue

        h = _content_hash(content)
        yyyymm = datetime.utcnow().strftime("%Y-%m")
        rel_path = f"{yyyymm}/{h}.html"  # relative to raw_pages dir
        _save_content(storage_obj, rel_path, content)

        r = session.execute(
            text("""
                INSERT INTO raw_pages (store_id, url, fetched_at, content_ref, content_hash, fetch_status)
                VALUES (:sid, :url, :fetched, :ref, :hash, 'success')
                RETURNING id
            """),
            {"sid": store["id"], "url": url, "fetched": datetime.utcnow(), "ref": rel_path, "hash": h},
        )
        pid = r.scalar()
        session.commit()
        pages.append({"id": pid, "store_id": store["id"], "url": url, "content_ref": rel_path})

    return pages


def _save_content(storage_obj, rel_path: str, content: str):
    raw_dir = storage_obj.get("raw_pages")
    if raw_dir is None:
        raw_dir = Path("./data/raw_pages")
    base = Path(raw_dir) if not isinstance(raw_dir, Path) else raw_dir
    path = base / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

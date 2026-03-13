"""HTTP fetcher for store pages."""
import hashlib
import logging
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

import httpx

from .db import get_session
from .storage import get_storage
from ..backend.src.models import Store, RawPage
from sqlalchemy import select

logger = logging.getLogger(__name__)

# Max pages per store per run (cost control)
MAX_PAGES_PER_STORE = 50


async def fetch_page(url: str) -> tuple[str, int, Optional[str]]:
    """
    Fetch a single page. Returns (content, status_code, error_message).
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text, resp.status_code, None
    except httpx.HTTPError as e:
        logger.warning("Fetch failed for %s: %s", url, str(e))
        return "", 0, str(e)


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


async def fetch_and_store(
    store_id: int,
    url: str,
    session,
    storage,
) -> tuple[bool, Optional[int]]:
    """
    Fetch page, store raw content, create RawPage record.
    Returns (success, raw_page_id).
    """
    content, status, err = await fetch_page(url)
    if err:
        return False, None

    h = content_hash(content)
    path = f"raw_pages/{datetime.utcnow().strftime('%Y-%m')}/{h}.html"
    storage.put(path, content.encode("utf-8"))

    raw = RawPage(
        store_id=store_id,
        url=url,
        fetched_at=datetime.utcnow(),
        content_ref=path,
        content_hash=h,
        fetch_status="success",
    )
    session.add(raw)
    session.commit()
    session.refresh(raw)
    return True, raw.id

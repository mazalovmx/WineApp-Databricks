from __future__ import annotations

from datetime import UTC, datetime


def utc_now_naive() -> datetime:
    """
    Return UTC datetime without tzinfo for compatibility with naive DB columns.
    """
    return datetime.now(UTC).replace(tzinfo=None)


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def utc_now_compact() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%S")

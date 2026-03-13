from __future__ import annotations

import base64
import hmac
import time

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.auth import (
    TOKEN_TTL_SECONDS,
    authenticate_user,
    ensure_default_users,
    hash_password,
    make_token,
    parse_token,
    verify_password,
)
from app.config import settings
from app.db import engine
from app.models import User


def test_hash_and_verify_password_roundtrip() -> None:
    salt = "unit-salt"
    digest = hash_password("secret-pass", salt)
    assert verify_password("secret-pass", salt, digest)
    assert not verify_password("wrong-pass", salt, digest)


def test_make_and_parse_token_roundtrip() -> None:
    token = make_token("A")
    assert parse_token(token) == "A"


def test_parse_token_rejects_invalid_payload() -> None:
    with pytest.raises(HTTPException) as exc:
        parse_token("not-a-valid-token")
    assert exc.value.status_code == 401
    assert "Invalid token" in str(exc.value.detail)


def test_parse_token_rejects_bad_signature() -> None:
    raw = "A:1234567890:bad-signature"
    token = base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")
    with pytest.raises(HTTPException) as exc:
        parse_token(token)
    assert exc.value.status_code == 401
    assert "signature" in str(exc.value.detail).lower()


def test_parse_token_rejects_expired_token() -> None:
    ts = int(time.time()) - TOKEN_TTL_SECONDS - 5
    payload = f"A:{ts}"
    signature = hmac.new(settings.app_secret.encode("utf-8"), payload.encode("utf-8"), "sha256").hexdigest()
    token = base64.urlsafe_b64encode(f"{payload}:{signature}".encode()).decode("ascii")

    with pytest.raises(HTTPException) as exc:
        parse_token(token)
    assert exc.value.status_code == 401
    assert "expired" in str(exc.value.detail).lower()


def test_authenticate_user_success_and_failure() -> None:
    with Session(engine) as session:
        ensure_default_users(session)
        assert authenticate_user(session, "A", "changeme-a")
        assert not authenticate_user(session, "A", "bad-password")
        assert not authenticate_user(session, "Z", "any")


def test_ensure_default_users_updates_existing_rows() -> None:
    with Session(engine) as session:
        row = session.get(User, "A")
        assert row is not None
        row.display_name = "Temp Name"
        row.locale = "ru"
        session.commit()

        ensure_default_users(session)
        updated = session.get(User, "A")
        assert updated is not None
        assert updated.display_name == settings.user_a_display_name
        assert updated.locale == "ru"


def test_default_users_have_product_display_names() -> None:
    with Session(engine) as session:
        ensure_default_users(session)
        user_a = session.get(User, "A")
        user_b = session.get(User, "B")
        assert user_a is not None
        assert user_b is not None
        assert user_a.display_name == settings.user_a_display_name
        assert user_b.display_name == settings.user_b_display_name

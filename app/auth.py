from __future__ import annotations

import base64
import hashlib
import hmac
import os
import time
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_session
from app.models import User

TOKEN_TTL_SECONDS = 60 * 60 * 24 * 14
security = HTTPBearer(auto_error=False)


def hash_password(password: str, salt: str) -> str:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return digest.hex()


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password, salt), expected_hash)


def make_token(user_id: str) -> str:
    now = int(time.time())
    payload = f"{user_id}:{now}"
    signature = hmac.new(settings.app_secret.encode("utf-8"), payload.encode("utf-8"), "sha256").hexdigest()
    token = base64.urlsafe_b64encode(f"{payload}:{signature}".encode()).decode("ascii")
    return token


def parse_token(token: str) -> str:
    try:
        raw = base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
        user_id, ts_raw, signature = raw.split(":", 2)
        ts = int(ts_raw)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.") from exc

    expected_sig = hmac.new(
        settings.app_secret.encode("utf-8"),
        f"{user_id}:{ts}".encode(),
        "sha256",
    ).hexdigest()
    if not hmac.compare_digest(signature, expected_sig):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token signature.")
    if int(time.time()) - ts > TOKEN_TTL_SECONDS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    return user_id


@dataclass(slots=True)
class AuthUser:
    id: str
    locale: str
    display_name: str


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(security),
    session: Session = Depends(get_session),
) -> AuthUser:
    if creds is None or not creds.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token.")
    user_id = parse_token(creds.credentials)
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user.")
    return AuthUser(id=user.id, locale=user.locale, display_name=user.display_name)


def ensure_default_users(session: Session) -> None:
    salt_a = os.getenv("USER_A_SALT", "salt-a")
    salt_b = os.getenv("USER_B_SALT", "salt-b")
    expected = {
        "A": (settings.user_a_display_name, "en", hash_password(settings.user_a_password, salt_a)),
        "B": (settings.user_b_display_name, "ru", hash_password(settings.user_b_password, salt_b)),
    }
    for user_id, (name, locale, pwd_hash) in expected.items():
        row = session.get(User, user_id)
        if row is None:
            session.add(
                User(
                    id=user_id,
                    display_name=name,
                    locale=locale,
                    password_hash=pwd_hash,
                )
            )
        else:
            # Preserve user-managed locale preference across restarts.
            row.display_name = name
            if row.locale not in {"en", "ru"}:
                row.locale = locale
            row.password_hash = pwd_hash
    session.commit()


def authenticate_user(session: Session, user_id: str, password: str) -> bool:
    salts = {"A": os.getenv("USER_A_SALT", "salt-a"), "B": os.getenv("USER_B_SALT", "salt-b")}
    user = session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        return False
    salt = salts.get(user_id, "salt-a")
    return verify_password(password, salt, user.password_hash)

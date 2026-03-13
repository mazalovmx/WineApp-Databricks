"""Simple authentication for two users (A and B)."""
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext

from backend.src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload["sub"]
    if user_id not in ("A", "B"):
        raise HTTPException(status_code=401, detail="Invalid user")
    return {"sub": user_id, "locale": payload.get("locale", "en")}


def get_user(user_id: str) -> Optional[dict]:
    """Get user by id - for internal use."""
    if user_id not in ("A", "B"):
        return None
    with __import__("backend.src.db", fromlist=["get_session"]).get_session() as session:
        from sqlalchemy import text
        r = session.execute(
            text("SELECT id, display_name, locale FROM users WHERE id = :id"),
            {"id": user_id},
        ).fetchone()
    if r:
        return {"id": r[0], "display_name": r[1], "locale": r[2]}
    return {"id": user_id, "display_name": f"User {user_id}", "locale": "en"}

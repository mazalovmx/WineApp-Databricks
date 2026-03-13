"""Authentication endpoints - simple email/password for two users."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.src.auth import create_access_token, verify_password, get_user
from backend.src.db import get_session
from sqlalchemy import text

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    user_id: str  # "A" or "B"
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    """Minimal auth: user_id A or B with password from env."""
    import os
    pw_a = os.getenv("USER_A_PASSWORD", "xK9mN2pQ7sL4vY8w")
    pw_b = os.getenv("USER_B_PASSWORD", "aB3cD6eF9gH2jK5mN")
    expected = pw_a if req.user_id.upper() == "A" else (pw_b if req.user_id.upper() == "B" else None)
    if expected is None:
        raise HTTPException(status_code=400, detail="Invalid user_id")
    # Support bcrypt hash in env, or plain text for dev
    if expected.startswith("$2b$") or expected.startswith("$2a$"):
        if not verify_password(req.password, expected):
            raise HTTPException(status_code=401, detail="Invalid credentials")
    elif req.password != expected:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": req.user_id.upper()})
    return TokenResponse(access_token=token, user_id=req.user_id.upper())

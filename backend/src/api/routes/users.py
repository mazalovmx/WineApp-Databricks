"""User endpoints."""
from fastapi import APIRouter, Depends
from backend.src.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    """Current user info."""
    return {
        "user_id": current_user["sub"],
        "locale": current_user.get("locale", "en"),
    }

import hashlib
from typing import Optional
from fastapi import HTTPException, Header, status
from app.core.config import settings


def generate_admin_token() -> str:
    """Generate a deterministic session hash based on the server's ADMIN_SECRET_KEY."""
    salt = "zap10x-internship-league-admin-salt"
    raw_signature = f"{settings.ADMIN_SECRET_KEY}:{salt}"
    return hashlib.sha256(raw_signature.encode("utf-8")).hexdigest()


def require_admin(
    authorization: Optional[str] = Header(None, description="Standard Bearer token"),
    x_admin_key: Optional[str] = Header(None, description="Direct Admin secret key")
) -> bool:
    """
    FastAPI security dependency to guard admin-only operations.
    Validates against the configured ADMIN_SECRET_KEY or generated session token.
    """
    valid_token = generate_admin_token()

    # 1. Check direct X-Admin-Key header
    if x_admin_key and x_admin_key == settings.ADMIN_SECRET_KEY:
        return True

    # 2. Check standard Authorization: Bearer <token>
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            provided_token = parts[1]
            if provided_token == valid_token or provided_token == settings.ADMIN_SECRET_KEY:
                return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized: Admin access required to perform this action.",
        headers={"WWW-Authenticate": "Bearer"}
    )

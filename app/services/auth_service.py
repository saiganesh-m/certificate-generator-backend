from fastapi import HTTPException, status
from app.core.config import settings
from app.core.security import generate_admin_token
from app.schemas.auth import AuthResponse


class AuthService:
    """Business logic for organizer and administrator authentication."""

    @staticmethod
    def verify_admin_passkey(provided_key: str) -> AuthResponse:
        """
        Validate the entered passkey against settings.ADMIN_SECRET_KEY.
        Returns a session token on success or raises 401 Unauthorized.
        """
        if not provided_key or not provided_key.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passkey cannot be empty."
            )

        if provided_key.strip() != settings.ADMIN_SECRET_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Admin Passkey. Please verify with your organization administrator."
            )

        session_token = generate_admin_token()
        return AuthResponse(
            success=True,
            message="Organizer authentication successful.",
            token=session_token
        )

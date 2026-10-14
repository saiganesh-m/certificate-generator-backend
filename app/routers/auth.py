from fastapi import APIRouter, Depends
from app.schemas.auth import VerifyKeyRequest, AuthResponse, AuthStatusResponse
from app.services.auth_service import AuthService
from app.core.security import require_admin

router = APIRouter(prefix="/auth", tags=["Authentication & Security"])


@router.post(
    "/verify-key",
    response_model=AuthResponse,
    summary="Verify Admin Passkey",
    description="Validates the organizer passkey against the server configuration and returns a session token."
)
def verify_admin_key(payload: VerifyKeyRequest):
    """Verify administrator passkey and return an authorization session token."""
    return AuthService.verify_admin_passkey(payload.passkey)


@router.get(
    "/check-status",
    response_model=AuthStatusResponse,
    summary="Check Admin Session Status",
    description="Validates whether the current authorization header or token grants administrative access."
)
def check_admin_status(is_admin: bool = Depends(require_admin)):
    """Check if the current caller session token is valid and active."""
    return AuthStatusResponse(authenticated=True, role="admin")

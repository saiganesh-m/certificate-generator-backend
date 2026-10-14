from typing import Optional
from pydantic import BaseModel, Field


class VerifyKeyRequest(BaseModel):
    """Payload for verifying the organizer admin passkey."""
    passkey: str = Field(..., min_length=1, description="The secret organizer admin passkey")


class AuthResponse(BaseModel):
    """Response returned upon successful passkey verification."""
    success: bool = Field(..., description="Whether authentication was successful")
    message: str = Field(..., description="Status message")
    token: Optional[str] = Field(None, description="Cryptographic session token for authorized requests")


class AuthStatusResponse(BaseModel):
    """Response for checking current session validity."""
    authenticated: bool = Field(..., description="Whether the caller has valid admin privileges")
    role: str = Field("admin", description="Current authorization role")

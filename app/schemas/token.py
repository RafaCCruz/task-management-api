"""Authentication / token schemas."""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """JWT token pair returned after successful login or refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded JWT payload."""

    sub: Optional[str] = None
    type: Optional[str] = None
    exp: Optional[int] = None


class LoginRequest(BaseModel):
    """Credentials for login."""

    email: EmailStr = Field(..., examples=["alice@example.com"])
    password: str = Field(..., examples=["Str0ngP@ssw0rd"])


class RefreshRequest(BaseModel):
    """Payload for refreshing an access token."""

    refresh_token: str

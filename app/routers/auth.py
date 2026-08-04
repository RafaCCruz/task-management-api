"""Authentication endpoints: register, login, refresh."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependencies import get_auth_service, get_user_service
from app.schemas.token import LoginRequest, RefreshRequest, Token
from app.schemas.user import UserCreate, UserRead
from app.services.auth import AuthService
from app.services.user import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account. The password is hashed with bcrypt before storage.",
)
def register(
    payload: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    user = service.register(payload)
    return UserRead.model_validate(user)


@router.post(
    "/login",
    response_model=Token,
    summary="Login and obtain JWT tokens",
    description="Authenticate with email and password. Returns an access token (short-lived) "
    "and a refresh token (longer-lived).",
)
def login(
    payload: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    return service.login(payload.email, payload.password)


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access + refresh token pair.",
)
def refresh(
    payload: RefreshRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    return service.refresh(payload.refresh_token)

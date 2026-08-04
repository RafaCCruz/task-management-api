"""User profile endpoints (authenticated)."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import CurrentUser, get_user_service
from app.schemas.user import UserRead, UserUpdate
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user profile",
)
def read_current_user(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UserRead,
    summary="Update current user profile",
    description="Partially update the authenticated user's name or password.",
)
def update_current_user(
    payload: UserUpdate,
    current_user: CurrentUser,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    user = service.update(current_user.id, payload)
    return UserRead.model_validate(user)

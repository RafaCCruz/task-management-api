"""Authentication service."""

from jose import JWTError
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.token import Token


class AuthService:
    """Handles login, token creation and token refresh."""

    def __init__(self, db: Session) -> None:
        self.user_repo = UserRepository(db)

    def authenticate(self, email: str, password: str) -> User:
        user = self.user_repo.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedException(message="Incorrect email or password")
        if not user.is_active:
            raise UnauthorizedException(message="Inactive user")
        return user

    def login(self, email: str, password: str) -> Token:
        user = self.authenticate(email, password)
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        return Token(access_token=access_token, refresh_token=refresh_token)

    def refresh(self, refresh_token: str) -> Token:
        try:
            payload = decode_token(refresh_token)
        except JWTError:
            raise UnauthorizedException(message="Invalid refresh token")

        if payload.get("type") != "refresh":
            raise UnauthorizedException(message="Invalid token type")

        user_id = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException(message="Invalid token payload")

        user = self.user_repo.get_by_id(int(user_id))
        if user is None or not user.is_active:
            raise UnauthorizedException(message="User not found or inactive")

        new_access = create_access_token(subject=user.id)
        new_refresh = create_refresh_token(subject=user.id)
        return Token(access_token=new_access, refresh_token=new_refresh)

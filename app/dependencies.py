"""FastAPI dependencies (auth, db session, services)."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedException
from app.core.security import decode_token
from app.database.session import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.services.task import TaskService
from app.services.user import UserService

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Extract and validate the JWT access token, then load the current user."""
    if credentials is None:
        raise UnauthorizedException(message="Not authenticated")

    token = credentials.credentials
    try:
        payload = decode_token(token)
    except JWTError:
        raise UnauthorizedException(message="Could not validate credentials")

    if payload.get("type") != "access":
        raise UnauthorizedException(message="Invalid token type")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException(message="Invalid token payload")

    user = UserRepository(db).get_by_id(int(user_id))
    if user is None or not user.is_active:
        raise UnauthorizedException(message="User not found or inactive")

    return user


# Type aliases for cleaner route signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]


def get_auth_service(db: DbSession) -> AuthService:
    return AuthService(db)


def get_user_service(db: DbSession) -> UserService:
    return UserService(db)


def get_task_service(db: DbSession) -> TaskService:
    return TaskService(db)

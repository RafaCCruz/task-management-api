"""User service – business rules around users."""

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Business logic for user registration and profile management."""

    def __init__(self, db: Session) -> None:
        self.user_repo = UserRepository(db)

    def register(self, data: UserCreate) -> User:
        existing = self.user_repo.get_by_email(data.email)
        if existing is not None:
            raise ConflictException(message="Email already registered")

        hashed = hash_password(data.password)
        return self.user_repo.create(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hashed,
        )

    def get_by_id(self, user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException(message="User not found")
        return user

    def update(self, user_id: int, data: UserUpdate) -> User:
        user = self.get_by_id(user_id)
        update_data = data.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))

        return self.user_repo.update(user, **update_data)

from sqlalchemy.orm import Session
from typing import List, Optional
from shared.db.repositories.user_repo import UserRepository
from shared.db.models.user import User
from shared.core.security import get_password_hash
from shared.core.errors import UserNotFoundError, UserAlreadyExistsError

class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def create_user(self, user_data: dict) -> User:
        """Create a new user with hashed password."""
        # Hash the password before storing
        if "password" in user_data:
            user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
        
        return self.user_repo.create(user_data)

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.user_repo.get_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.user_repo.get_by_email(email)

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        return self.user_repo.get_all(skip=skip, limit=limit)

    def update_user(self, user_id: int, user_data: dict) -> Optional[User]:
        """Update user."""
        # Hash password if it's being updated
        if "password" in user_data:
            user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
        
        return self.user_repo.update(user_id, user_data)

    def delete_user(self, user_id: int) -> bool:
        """Delete user."""
        return self.user_repo.delete(user_id)

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user."""
        return self.user_repo.authenticate(email, password)

    def change_password(self, user_id: int, new_password: str) -> Optional[User]:
        """Change user password."""
        hashed_password = get_password_hash(new_password)
        return self.user_repo.update(user_id, {"hashed_password": hashed_password})

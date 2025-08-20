from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from shared.db.models.user import User
from shared.core.errors import UserNotFoundError, UserAlreadyExistsError

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_data: dict) -> User:
        """Create a new user."""
        try:
            user = User(**user_data)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise UserAlreadyExistsError(user_data.get("email", "unknown"))

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        return self.db.query(User).offset(skip).limit(limit).all()

    def update(self, user_id: int, user_data: dict) -> Optional[User]:
        """Update user."""
        user = self.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(str(user_id))
        
        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        """Delete user."""
        user = self.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(str(user_id))
        
        self.db.delete(user)
        self.db.commit()
        return True

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        from shared.core.security import verify_password
        
        user = self.get_by_email(email)
        if user and verify_password(password, user.hashed_password):
            return user
        return None

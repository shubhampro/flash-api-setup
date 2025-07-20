# NEW MODULE DEVELOPMENT GUIDE

## 🚀 **Creating New Modules in FastAPI Multi-Database Application**

This guide covers the complete process of adding new modules to your multi-database FastAPI application, including migrations, models, routers, services, and test cases.

---

## 📋 **Table of Contents**

1. [Migrations - Table Creation & Alter](#migrations)
2. [Model Creation](#models)
3. [Router Development](#routers)
4. [Services Layer](#services)
5. [Test Cases](#tests)
6. [Complete Example](#example)

---

## 🗄️ **1. Migrations - Table Creation & Alter**

### **Alembic Setup (if not already configured)**
```bash
# Initialize Alembic
alembic init app/db/migrations

# Update alembic.ini
sqlalchemy.url = mysql+pymysql://user:password@localhost/mono_api_main
```

### **Creating New Migration**
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add user module"

# Create empty migration
alembic revision -m "Add user module"
```

### **Migration File Structure**
```python
# app/db/migrations/versions/xxx_add_user_module.py
"""Add user module

Revision ID: xxx
Revises: previous_revision
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])

def downgrade():
    op.drop_table('users')
```

### **Running Migrations**
```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>

# Rollback one migration
alembic downgrade -1

# Check current status
alembic current
```

---

## 🏗️ **2. Model Creation**

### **Choose the Right Base Class**
```python
# For main application data
from app.db.base import BaseModel

# For analytics data
from app.db.base import AnalyticsBaseModel

# For logs data
from app.db.base import LogsBaseModel
```

### **Main Database Model Example**
```python
# app/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.db.base import BaseModel

class User(BaseModel):
    """User model for main application database."""
    
    __tablename__ = "users"
    
    email = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(100), nullable=False, unique=True, index=True)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    bio = Column(Text, nullable=True)
    
    # Relationships
    items = relationship("Item", back_populates="owner")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
```

### **Analytics Database Model Example**
```python
# app/models/user_analytics.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db.base import AnalyticsBaseModel

class UserLogin(AnalyticsBaseModel):
    """User login tracking for analytics."""
    
    __tablename__ = "user_logins"
    
    user_id = Column(Integer, nullable=False, index=True)
    login_method = Column(String(50), nullable=False)  # email, oauth, etc.
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    success = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<UserLogin(id={self.id}, user_id={self.user_id})>"
```

### **Logs Database Model Example**
```python
# app/models/user_logs.py
from sqlalchemy import Column, Integer, String, Text, Enum
from app.db.base import LogsBaseModel
import enum

class UserAction(enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"

class UserAuditLog(LogsBaseModel):
    """User audit logs for compliance."""
    
    __tablename__ = "user_audit_logs"
    
    user_id = Column(Integer, nullable=False, index=True)
    action = Column(Enum(UserAction), nullable=False)
    details = Column(Text, nullable=True)
    performed_by = Column(Integer, nullable=True)  # admin user who performed action
    
    def __repr__(self):
        return f"<UserAuditLog(id={self.id}, user_id={self.user_id}, action={self.action})>"
```

### **Update Models __init__.py**
```python
# app/models/__init__.py
# Main database models
from .user import User

# Analytics database models
from .user_analytics import UserLogin

# Logs database models
from .user_logs import UserAuditLog, UserAction

__all__ = [
    # Main models
    "User",
    # Analytics models
    "UserLogin",
    # Logs models
    "UserAuditLog",
    "UserAction"
]
```

---

## 🌐 **3. Router Development**

### **Create Pydantic Schemas**
```python
# app/api/v1/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    is_active: Optional[bool] = None

class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserList(BaseModel):
    users: list[UserRead]
    total: int
```

### **Create Router**
```python
# app/api/v1/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_main_db
from app.services.user_service import UserService
from app.services.logging_service import LoggingService
from app.models.logs import LogLevel
from app.api.v1.schemas.user import UserCreate, UserUpdate, UserRead, UserList
from app.utils.pagination import CursorPage

router = APIRouter()

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_main_db)
):
    """Create a new user."""
    try:
        new_user = UserService.create_user(db, user)
        
        # Log to logs database
        LoggingService.log_application_event(
            level=LogLevel.INFO,
            message=f"User created: {new_user.email}",
            logger_name="users",
            module="users",
            function="create_user"
        )
        
        return new_user
    except Exception as e:
        LoggingService.log_exception(e, "users", "users", "create_user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.get("/", response_model=CursorPage[UserRead])
def get_users(
    limit: int = Query(20, le=100, description="Number of users to return"),
    after: Optional[str] = Query(None, description="Cursor for pagination"),
    db: Session = Depends(get_main_db)
):
    """Get users with cursor pagination."""
    try:
        users = UserService.get_users(db, limit=limit, after=after)
        return users
    except Exception as e:
        LoggingService.log_exception(e, "users", "users", "get_users")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_main_db)
):
    """Get a specific user by ID."""
    try:
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        LoggingService.log_exception(e, "users", "users", "get_user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )

@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_main_db)
):
    """Update a user."""
    try:
        updated_user = UserService.update_user(db, user_id, user_update)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Log to logs database
        LoggingService.log_application_event(
            level=LogLevel.INFO,
            message=f"User updated: {updated_user.email}",
            logger_name="users",
            module="users",
            function="update_user"
        )
        
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        LoggingService.log_exception(e, "users", "users", "update_user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_main_db)
):
    """Delete a user."""
    try:
        success = UserService.delete_user(db, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Log to logs database
        LoggingService.log_application_event(
            level=LogLevel.INFO,
            message=f"User deleted: ID {user_id}",
            logger_name="users",
            module="users",
            function="delete_user"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        LoggingService.log_exception(e, "users", "users", "delete_user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
```

### **Register Router**
```python
# app/api/v1/__init__.py
from fastapi import APIRouter
from .routers import items, analytics, users

api_router = APIRouter()

# Include routers
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
```

---

## 🔧 **4. Services Layer**

### **Main Database Service**
```python
# app/services/user_service.py
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.models.user import User
from app.api.v1.schemas.user import UserCreate, UserUpdate
from app.utils.security import get_password_hash
from app.utils.pagination import CursorPage, create_cursor_page
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Service for user database operations."""
    
    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == user_create.email) | 
            (User.username == user_create.username)
        ).first()
        
        if existing_user:
            raise ValueError("User with this email or username already exists")
        
        # Create new user
        hashed_password = get_password_hash(user_create.password)
        db_user = User(
            email=user_create.email,
            username=user_create.username,
            full_name=user_create.full_name,
            bio=user_create.bio,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"Created user: {db_user.email}")
        return db_user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_users(
        db: Session, 
        limit: int = 20, 
        after: Optional[str] = None
    ) -> CursorPage[User]:
        """Get users with cursor pagination."""
        query = db.query(User).filter(User.is_active == True)
        
        if after:
            # Decode cursor and apply filter
            cursor_data = decode_cursor(after)
            query = query.filter(User.id > cursor_data["id"])
        
        users = query.order_by(User.id).limit(limit + 1).all()
        
        has_more = len(users) > limit
        if has_more:
            users = users[:-1]
        
        return create_cursor_page(
            items=users,
            has_more=has_more,
            cursor_field="id"
        )
    
    @staticmethod
    def update_user(
        db: Session, 
        user_id: int, 
        user_update: UserUpdate
    ) -> Optional[User]:
        """Update user."""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"Updated user: {db_user.email}")
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete user (soft delete)."""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False
        
        db_user.is_active = False
        db.commit()
        
        logger.info(f"Deleted user: {db_user.email}")
        return True
```

### **Analytics Service**
```python
# app/services/user_analytics_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from app.models.user_analytics import UserLogin
from app.db.session import get_analytics_db
import logging

logger = logging.getLogger(__name__)

class UserAnalyticsService:
    """Service for user analytics database operations."""
    
    @staticmethod
    def log_user_login(
        user_id: int,
        login_method: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True
    ) -> UserLogin:
        """Log user login to analytics database."""
        with next(get_analytics_db()) as db:
            login = UserLogin(
                user_id=user_id,
                login_method=login_method,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success
            )
            db.add(login)
            db.commit()
            db.refresh(login)
            
            logger.info(f"Logged user login: user_id={user_id}, method={login_method}")
            return login
    
    @staticmethod
    def get_login_stats(user_id: Optional[int] = None, days: int = 30) -> dict:
        """Get login statistics."""
        with next(get_analytics_db()) as db:
            query = db.query(
                func.count(UserLogin.id).label('total_logins'),
                func.count(UserLogin.id).filter(UserLogin.success == True).label('successful_logins'),
                func.count(UserLogin.id).filter(UserLogin.success == False).label('failed_logins')
            )
            
            if user_id:
                query = query.filter(UserLogin.user_id == user_id)
            
            # Add date filter for last N days
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            query = query.filter(UserLogin.created_at >= cutoff_date)
            
            result = query.first()
            
            return {
                "total_logins": result.total_logins,
                "successful_logins": result.successful_logins,
                "failed_logins": result.failed_logins,
                "success_rate": (result.successful_logins / result.total_logins * 100) if result.total_logins > 0 else 0
            }
```

### **Logging Service Extension**
```python
# app/services/user_logging_service.py
from app.services.logging_service import LoggingService
from app.models.logs import LogLevel, UserAuditLog, UserAction
from app.db.session import get_logs_db
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class UserLoggingService:
    """Service for user-specific logging operations."""
    
    @staticmethod
    def log_user_action(
        user_id: int,
        action: UserAction,
        details: Optional[str] = None,
        performed_by: Optional[int] = None
    ) -> UserAuditLog:
        """Log user action to logs database."""
        with next(get_logs_db()) as db:
            audit_log = UserAuditLog(
                user_id=user_id,
                action=action,
                details=details,
                performed_by=performed_by
            )
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)
            
            logger.info(f"Logged user action: user_id={user_id}, action={action.value}")
            return audit_log
    
    @staticmethod
    def get_user_audit_logs(
        user_id: Optional[int] = None,
        action: Optional[UserAction] = None,
        limit: int = 100
    ) -> List[UserAuditLog]:
        """Get user audit logs."""
        with next(get_logs_db()) as db:
            query = db.query(UserAuditLog)
            
            if user_id:
                query = query.filter(UserAuditLog.user_id == user_id)
            
            if action:
                query = query.filter(UserAuditLog.action == action)
            
            logs = query.order_by(desc(UserAuditLog.created_at)).limit(limit).all()
            return logs
```

---

## 🧪 **5. Test Cases**

### **Test Configuration**
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.core.config import settings

# Test database URL
TEST_DATABASE_URL = "mysql+pymysql://test_user:test_pass@localhost/test_mono_api"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client():
    return TestClient(app)
```

### **Model Tests**
```python
# tests/test_models/test_user.py
import pytest
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.user_service import UserService
from app.api.v1.schemas.user import UserCreate

class TestUserModel:
    def test_create_user(self, db_session: Session):
        """Test user creation."""
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpass123",
            full_name="Test User"
        )
        
        user = UserService.create_user(db_session, user_data)
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.is_active == True
        assert user.id is not None
    
    def test_user_repr(self, db_session: Session):
        """Test user string representation."""
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        
        user = UserService.create_user(db_session, user_data)
        assert "test@example.com" in str(user)
```

### **Service Tests**
```python
# tests/test_services/test_user_service.py
import pytest
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.api.v1.schemas.user import UserCreate, UserUpdate
from app.models.user import User

class TestUserService:
    def test_create_user_success(self, db_session: Session):
        """Test successful user creation."""
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        
        user = UserService.create_user(db_session, user_data)
        assert user.email == "test@example.com"
        assert user.username == "testuser"
    
    def test_create_user_duplicate_email(self, db_session: Session):
        """Test user creation with duplicate email."""
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        
        # Create first user
        UserService.create_user(db_session, user_data)
        
        # Try to create second user with same email
        user_data2 = UserCreate(
            email="test@example.com",
            username="testuser2",
            password="testpass123"
        )
        
        with pytest.raises(ValueError, match="already exists"):
            UserService.create_user(db_session, user_data2)
    
    def test_get_user_by_id(self, db_session: Session):
        """Test getting user by ID."""
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        
        created_user = UserService.create_user(db_session, user_data)
        retrieved_user = UserService.get_user_by_id(db_session, created_user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"
    
    def test_update_user(self, db_session: Session):
        """Test user update."""
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        
        user = UserService.create_user(db_session, user_data)
        
        update_data = UserUpdate(full_name="Updated Name", bio="New bio")
        updated_user = UserService.update_user(db_session, user.id, update_data)
        
        assert updated_user.full_name == "Updated Name"
        assert updated_user.bio == "New bio"
    
    def test_delete_user(self, db_session: Session):
        """Test user deletion (soft delete)."""
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        
        user = UserService.create_user(db_session, user_data)
        success = UserService.delete_user(db_session, user.id)
        
        assert success == True
        
        # Check that user is soft deleted
        deleted_user = UserService.get_user_by_id(db_session, user.id)
        assert deleted_user.is_active == False
```

### **API Tests**
```python
# tests/test_api/test_users.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestUsersAPI:
    def test_create_user_success(self):
        """Test successful user creation via API."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "full_name": "Test User"
        }
        
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert data["full_name"] == "Test User"
        assert "id" in data
    
    def test_create_user_duplicate_email(self):
        """Test user creation with duplicate email via API."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123"
        }
        
        # Create first user
        client.post("/api/v1/users/", json=user_data)
        
        # Try to create second user with same email
        user_data2 = {
            "email": "test@example.com",
            "username": "testuser2",
            "password": "testpass123"
        }
        
        response = client.post("/api/v1/users/", json=user_data2)
        assert response.status_code == 500
    
    def test_get_users(self):
        """Test getting users list."""
        response = client.get("/api/v1/users/")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "next_cursor" in data
    
    def test_get_user_by_id(self):
        """Test getting user by ID."""
        # First create a user
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123"
        }
        
        create_response = client.post("/api/v1/users/", json=user_data)
        user_id = create_response.json()["id"]
        
        # Get the user
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == "test@example.com"
    
    def test_get_user_not_found(self):
        """Test getting non-existent user."""
        response = client.get("/api/v1/users/99999")
        assert response.status_code == 404
    
    def test_update_user(self):
        """Test user update via API."""
        # First create a user
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123"
        }
        
        create_response = client.post("/api/v1/users/", json=user_data)
        user_id = create_response.json()["id"]
        
        # Update the user
        update_data = {
            "full_name": "Updated Name",
            "bio": "New bio"
        }
        
        response = client.put(f"/api/v1/users/{user_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["bio"] == "New bio"
    
    def test_delete_user(self):
        """Test user deletion via API."""
        # First create a user
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123"
        }
        
        create_response = client.post("/api/v1/users/", json=user_data)
        user_id = create_response.json()["id"]
        
        # Delete the user
        response = client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 204
        
        # Verify user is deleted (should return 404)
        get_response = client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 404
```

### **Integration Tests**
```python
# tests/test_integration/test_user_workflow.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestUserWorkflow:
    def test_complete_user_workflow(self):
        """Test complete user workflow: create, read, update, delete."""
        # 1. Create user
        user_data = {
            "email": "workflow@example.com",
            "username": "workflowuser",
            "password": "testpass123",
            "full_name": "Workflow User"
        }
        
        create_response = client.post("/api/v1/users/", json=user_data)
        assert create_response.status_code == 201
        
        user_id = create_response.json()["id"]
        
        # 2. Read user
        read_response = client.get(f"/api/v1/users/{user_id}")
        assert read_response.status_code == 200
        assert read_response.json()["email"] == "workflow@example.com"
        
        # 3. Update user
        update_data = {
            "full_name": "Updated Workflow User",
            "bio": "This is a test bio"
        }
        
        update_response = client.put(f"/api/v1/users/{user_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["full_name"] == "Updated Workflow User"
        
        # 4. Verify update
        verify_response = client.get(f"/api/v1/users/{user_id}")
        assert verify_response.status_code == 200
        assert verify_response.json()["bio"] == "This is a test bio"
        
        # 5. Delete user
        delete_response = client.delete(f"/api/v1/users/{user_id}")
        assert delete_response.status_code == 204
        
        # 6. Verify deletion
        final_response = client.get(f"/api/v1/users/{user_id}")
        assert final_response.status_code == 404
```

### **Running Tests**
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api/test_users.py

# Run with coverage
pytest --cov=app tests/

# Run with verbose output
pytest -v

# Run specific test class
pytest tests/test_api/test_users.py::TestUsersAPI

# Run specific test method
pytest tests/test_api/test_users.py::TestUsersAPI::test_create_user_success
```

---

## 📝 **6. Complete Example: User Module**

### **File Structure**
```
app/
├── models/
│   ├── user.py                    # Main database model
│   ├── user_analytics.py          # Analytics database model
│   └── user_logs.py               # Logs database model
├── api/v1/
│   ├── schemas/
│   │   └── user.py                # Pydantic schemas
│   └── routers/
│       └── users.py               # API endpoints
├── services/
│   ├── user_service.py            # Main database service
│   ├── user_analytics_service.py  # Analytics service
│   └── user_logging_service.py    # Logging service
└── db/migrations/
    └── versions/
        └── xxx_add_user_module.py # Database migration

tests/
├── test_models/
│   └── test_user.py               # Model tests
├── test_services/
│   └── test_user_service.py       # Service tests
├── test_api/
│   └── test_users.py              # API tests
└── test_integration/
    └── test_user_workflow.py      # Integration tests
```

### **Development Workflow**
1. **Create Migration**: `alembic revision --autogenerate -m "Add user module"`
2. **Create Models**: Define models for all three databases
3. **Create Schemas**: Define Pydantic schemas for API
4. **Create Services**: Implement business logic
5. **Create Router**: Implement API endpoints
6. **Write Tests**: Create comprehensive test suite
7. **Run Tests**: Ensure everything works
8. **Apply Migration**: `alembic upgrade head`
9. **Test API**: Verify endpoints work correctly

---

## 🎯 **Best Practices**

### **Database Design**
- Use appropriate base classes for different databases
- Add proper indexes for performance
- Use foreign keys for relationships
- Implement soft deletes where appropriate

### **API Design**
- Use consistent naming conventions
- Implement proper error handling
- Add comprehensive validation
- Use cursor pagination for large datasets

### **Service Layer**
- Keep business logic in services
- Use dependency injection
- Implement proper error handling
- Add comprehensive logging

### **Testing**
- Write tests for all layers
- Use fixtures for test data
- Test both success and failure cases
- Maintain high test coverage

### **Security**
- Validate all inputs
- Use proper authentication/authorization
- Log security-relevant events
- Implement rate limiting

---

## 🚀 **Quick Start Checklist**

- [ ] **Migrations**: Create and run database migrations
- [ ] **Models**: Define models for all three databases
- [ ] **Schemas**: Create Pydantic schemas for API
- [ ] **Services**: Implement business logic layer
- [ ] **Routers**: Create API endpoints
- [ ] **Tests**: Write comprehensive test suite
- [ ] **Documentation**: Update API documentation
- [ ] **Integration**: Test with existing modules

This guide provides a comprehensive framework for adding new modules to your multi-database FastAPI application. Follow these patterns to maintain consistency and quality across your codebase. 
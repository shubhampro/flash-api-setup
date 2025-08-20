import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.db.base import Base, get_db
from main import app

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the get_db dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def setup_database():
    """Setup test database before each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_user(setup_database):
    """Test creating a new user."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpass123"
    }
    
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
    
    user = response.json()
    assert user["email"] == user_data["email"]
    assert user["username"] == user_data["username"]
    assert user["full_name"] == user_data["full_name"]
    assert "id" in user

def test_get_users(setup_database):
    """Test getting all users."""
    # First create a user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    client.post("/api/v1/users/", json=user_data)
    
    # Then get all users
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    
    users = response.json()
    assert "users" in users
    assert len(users["users"]) == 1

def test_user_login(setup_database):
    """Test user login."""
    # First create a user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    client.post("/api/v1/users/", json=user_data)
    
    # Then try to login
    login_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    response = client.post("/api/v1/users/login", json=login_data)
    assert response.status_code == 200
    
    login_response = response.json()
    assert "token" in login_response
    assert "user" in login_response
    assert login_response["token"]["access_token"] is not None

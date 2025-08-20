from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from shared.db.base import get_db
from shared.services.user_service import UserService
from shared.core.security import create_access_token
from shared.core.errors import UserNotFoundError, UserAlreadyExistsError
from apps.api.schemas.user_in import UserCreate, UserUpdate, UserLogin
from apps.api.schemas.user_out import UserResponse, UserListResponse, UserLoginResponse, TokenResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    try:
        user_service = UserService(db)
        user_data = user.dict()
        created_user = user_service.create_user(user_data)
        return created_user
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("/", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all users with pagination."""
    user_service = UserService(db)
    users = user_service.get_users(skip=skip, limit=limit)
    total = len(users)  # In a real app, you'd get total count from DB
    
    return UserListResponse(
        users=users,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update user."""
    try:
        user_service = UserService(db)
        user_data = user_update.dict(exclude_unset=True)
        updated_user = user_service.update_user(user_id, user_data)
        return updated_user
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user."""
    try:
        user_service = UserService(db)
        user_service.delete_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/login", response_model=UserLoginResponse)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """User login."""
    user_service = UserService(db)
    user = user_service.authenticate_user(user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return UserLoginResponse(
        user=user,
        token=TokenResponse(
            access_token=access_token,
            expires_in=30 * 60  # 30 minutes in seconds
        )
    )

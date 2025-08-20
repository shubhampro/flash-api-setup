from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List
from shared.db.base import get_db
from shared.services.user_service import UserService
from shared.core.security import get_current_user_id
from shared.core.errors import UserNotFoundError
from apps.api.v2.schemas.user_out import UserResponseV2, UserListResponseV2

router = APIRouter(prefix="/users", tags=["users-v2"])

async def get_current_user_id_dependency(
    authorization: HTTPBearer = Depends()
):
    """Get current user ID from JWT token."""
    from shared.core.security import get_current_user_id
    user_id = get_current_user_id(authorization.credentials)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return int(user_id)

@router.get("/", response_model=UserListResponseV2)
async def get_users_v2(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    active_only: bool = Query(True, description="Filter only active users"),
    db: Session = Depends(get_db)
):
    """Get all users with enhanced V2 features."""
    user_service = UserService(db)
    users = user_service.get_users(skip=skip, limit=limit)
    
    # Filter active users if requested
    if active_only:
        users = [user for user in users if user.is_active]
    
    # Calculate if there are more users
    has_more = len(users) == limit
    
    # Convert to V2 response format
    users_v2 = []
    for user in users:
        # In a real app, you'd get these from the database
        profile_complete = bool(user.full_name)
        last_login = None  # This would come from a login tracking table
        login_count = 0    # This would come from a login tracking table
        
        user_v2 = UserResponseV2(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
            profile_complete=profile_complete,
            last_login=last_login,
            login_count=login_count
        )
        users_v2.append(user_v2)
    
    return UserListResponseV2(
        users=users_v2,
        total=len(users_v2),
        skip=skip,
        limit=limit,
        has_more=has_more
    )

@router.get("/{user_id}", response_model=UserResponseV2)
async def get_user_v2(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id_dependency)
):
    """Get user by ID with V2 enhanced response."""
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check if user is requesting their own data or is admin
    if user_id != current_user_id:
        # In a real app, you'd check admin permissions here
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Convert to V2 response format
    profile_complete = bool(user.full_name)
    last_login = None  # This would come from a login tracking table
    login_count = 0    # This would come from a login tracking table
    
    return UserResponseV2(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        updated_at=user.updated_at,
        profile_complete=profile_complete,
        last_login=last_login,
        login_count=login_count
    )

@router.get("/me/profile", response_model=UserResponseV2)
async def get_my_profile(
    current_user_id: int = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Get current user's profile with V2 enhanced response."""
    user_service = UserService(db)
    user = user_service.get_user(current_user_id)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Convert to V2 response format
    profile_complete = bool(user.full_name)
    last_login = None  # This would come from a login tracking table
    login_count = 0    # This would come from a login tracking table
    
    return UserResponseV2(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        updated_at=user.updated_at,
        profile_complete=profile_complete,
        last_login=last_login,
        login_count=login_count
    )

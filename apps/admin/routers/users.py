from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List
from shared.db.base import get_db
from shared.services.user_service import UserService
from shared.core.security import get_current_user_id
from shared.core.errors import UserNotFoundError
from apps.api.schemas.user_in import UserUpdate
from apps.api.schemas.user_out import UserResponse, UserListResponse

router = APIRouter(prefix="/users", tags=["admin-users"])

async def get_admin_user(
    authorization: HTTPBearer = Depends()
):
    """Get current admin user from JWT token."""
    from shared.core.security import get_current_user_id
    user_id = get_current_user_id(authorization.credentials)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    # Get user from database to check admin status
    db = next(get_db())
    user_service = UserService(db)
    user = user_service.get_user(int(user_id))
    
    if not user or not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    return user

@router.get("/", response_model=UserListResponse)
async def get_all_users_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    include_inactive: bool = Query(False, description="Include inactive users"),
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """Get all users (admin only)."""
    user_service = UserService(db)
    users = user_service.get_users(skip=skip, limit=limit)
    
    # Filter inactive users if not requested
    if not include_inactive:
        users = [user for user in users if user.is_active]
    
    return UserListResponse(
        users=users,
        total=len(users),
        skip=skip,
        limit=limit
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """Get user by ID (admin only)."""
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user_admin(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """Update user (admin only)."""
    try:
        user_service = UserService(db)
        user_data = user_update.dict(exclude_unset=True)
        updated_user = user_service.update_user(user_id, user_data)
        return updated_user
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """Delete user (admin only)."""
    try:
        user_service = UserService(db)
        user_service.delete_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """Activate user (admin only)."""
    try:
        user_service = UserService(db)
        updated_user = user_service.update_user(user_id, {"is_active": True})
        return updated_user
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """Deactivate user (admin only)."""
    try:
        user_service = UserService(db)
        updated_user = user_service.update_user(user_id, {"is_active": False})
        return updated_user
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/{user_id}/make-admin", response_model=UserResponse)
async def make_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """Make user an admin (admin only)."""
    try:
        user_service = UserService(db)
        updated_user = user_service.update_user(user_id, {"is_superuser": True})
        return updated_user
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/{user_id}/remove-admin", response_model=UserResponse)
async def remove_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """Remove admin privileges from user (admin only)."""
    try:
        user_service = UserService(db)
        updated_user = user_service.update_user(user_id, {"is_superuser": False})
        return updated_user
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

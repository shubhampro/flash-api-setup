from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from shared.db.base import get_db
from shared.services.user_service import UserService
from shared.core.security import verify_token, get_current_user_id
from shared.core.errors import AuthenticationError
from apps.api.schemas.user_out import UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user."""
    token = credentials.credentials
    user_id = get_current_user_id(token)
    
    if not user_id:
        raise AuthenticationError()
    
    user_service = UserService(db)
    user = user_service.get_user(int(user_id))
    
    if not user:
        raise AuthenticationError()
    
    return user

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information."""
    return current_user

@router.post("/verify")
async def verify_token_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Verify JWT token."""
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise AuthenticationError()
    
    return {"valid": True, "user_id": payload.get("sub")}

@router.post("/refresh")
async def refresh_token(
    current_user = Depends(get_current_user)
):
    """Refresh access token."""
    from shared.core.security import create_access_token
    
    new_token = create_access_token(data={"sub": str(current_user.id)})
    
    return {
        "access_token": new_token,
        "token_type": "bearer",
        "expires_in": 30 * 60  # 30 minutes in seconds
    }

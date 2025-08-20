from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserResponseV2(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Additional V2 fields
    profile_complete: bool = Field(description="Whether user profile is complete")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    login_count: int = Field(0, description="Total number of logins")

    class Config:
        from_attributes = True

class UserListResponseV2(BaseModel):
    users: list[UserResponseV2]
    total: int
    skip: int
    limit: int
    has_more: bool = Field(description="Whether there are more users to fetch")

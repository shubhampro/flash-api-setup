"""
Pydantic schemas for Item model.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    """Base schema for Item with common fields."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Item name")
    description: Optional[str] = Field(None, description="Item description")


class ItemCreate(ItemBase):
    """Schema for creating a new item."""
    pass


class ItemUpdate(BaseModel):
    """Schema for updating an existing item."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Item name")
    description: Optional[str] = Field(None, description="Item description")


class ItemRead(ItemBase):
    """Schema for reading item data."""
    
    id: int = Field(..., description="Item ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ItemResponse(BaseModel):
    """Response schema for single item operations."""
    
    success: bool = Field(..., description="Operation success status")
    data: Optional[ItemRead] = Field(None, description="Item data")
    message: Optional[str] = Field(None, description="Response message") 
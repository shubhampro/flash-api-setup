"""
Items API router with CRUD operations and cursor pagination.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.item_service import ItemService
from app.api.v1.schemas.item import ItemCreate, ItemRead, ItemUpdate, ItemResponse
from app.utils.pagination import CursorParams, CursorPage
from app.utils.exceptions import ItemNotFoundException

router = APIRouter()


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db)
) -> ItemRead:
    """
    Create a new item.
    
    Args:
        item_data: Item creation data
        db: Database session
    
    Returns:
        The created item
    """
    item_service = ItemService()
    item = item_service.create_item(db, item_data)
    return ItemRead.from_orm(item)


@router.get("/", response_model=CursorPage[ItemRead])
def list_items(
    after: str = None,
    limit: int = 20,
    db: Session = Depends(get_db)
) -> CursorPage[ItemRead]:
    """
    List items with cursor-based pagination.
    
    Args:
        after: Cursor for pagination (base64 encoded)
        limit: Maximum number of items to return (1-100)
        db: Database session
    
    Returns:
        CursorPage with items and next cursor
    """
    cursor_params = CursorParams(after=after, limit=limit)
    item_service = ItemService()
    result = item_service.get_items_paginated(db, cursor_params)
    
    # Convert SQLAlchemy models to Pydantic models
    items = [ItemRead.from_orm(item) for item in result.items]
    
    return CursorPage[ItemRead](
        items=items,
        next_cursor=result.next_cursor
    )


@router.get("/{item_id}", response_model=ItemRead)
def get_item(
    item_id: int,
    db: Session = Depends(get_db)
) -> ItemRead:
    """
    Get a specific item by ID.
    
    Args:
        item_id: Item ID
        db: Database session
    
    Returns:
        The item data
    
    Raises:
        HTTPException: If item not found
    """
    item_service = ItemService()
    item = item_service.get_item(db, item_id)
    
    if not item:
        raise ItemNotFoundException(item_id)
    
    return ItemRead.from_orm(item)


@router.put("/{item_id}", response_model=ItemRead)
def update_item(
    item_id: int,
    item_data: ItemUpdate,
    db: Session = Depends(get_db)
) -> ItemRead:
    """
    Update an existing item.
    
    Args:
        item_id: Item ID to update
        item_data: Update data
        db: Database session
    
    Returns:
        The updated item
    
    Raises:
        HTTPException: If item not found
    """
    item_service = ItemService()
    item = item_service.update_item(db, item_id, item_data)
    
    if not item:
        raise ItemNotFoundException(item_id)
    
    return ItemRead.from_orm(item)


@router.delete("/{item_id}", response_model=ItemResponse)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db)
) -> ItemResponse:
    """
    Delete an item by ID.
    
    Args:
        item_id: Item ID to delete
        db: Database session
    
    Returns:
        Success response
    
    Raises:
        HTTPException: If item not found
    """
    item_service = ItemService()
    item = item_service.delete_item(db, item_id)
    
    if not item:
        raise ItemNotFoundException(item_id)
    
    return ItemResponse(
        success=True,
        data=ItemRead.from_orm(item),
        message=f"Item {item_id} deleted successfully"
    ) 
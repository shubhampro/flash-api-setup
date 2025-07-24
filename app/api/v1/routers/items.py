"""
Items API router with CRUD operations and cursor pagination.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.item_service import ItemService
from app.api.v1.schemas.item import ItemCreate, ItemRead, ItemUpdate
from app.utils.pagination import CursorParams, CursorPage
from app.utils.exceptions import ItemNotFoundException
from app.utils.dependencies import RequestID
from app.api.v1.schemas.response import (
    SuccessResponse,
    PaginatedResponse,
    DeleteResponse,
    PaginationMeta,
    create_success_response,
    create_paginated_response,
    create_delete_response
)

router = APIRouter()


@router.post("/", response_model=SuccessResponse[ItemRead], status_code=status.HTTP_201_CREATED)
def create_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    request_id: str = RequestID
) -> SuccessResponse[ItemRead]:
    """
    Create a new item.
    
    Args:
        item_data: Item creation data
        db: Database session
        request_id: Request ID for tracking
    
    Returns:
        Success response with created item
    """
    item_service = ItemService()
    item = item_service.create_item(db, item_data)
    item_read = ItemRead.from_orm(item)
    
    return create_success_response(
        data=item_read,
        message="Item created successfully",
        request_id=request_id
    )


@router.get("/", response_model=PaginatedResponse[ItemRead])
def list_items(
    after: str = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    request_id: str = RequestID
) -> PaginatedResponse[ItemRead]:
    """
    List items with cursor-based pagination.
    
    Args:
        after: Cursor for pagination (base64 encoded)
        limit: Maximum number of items to return (1-100)
        db: Database session
        request_id: Request ID for tracking
    
    Returns:
        Paginated response with items
    """
    cursor_params = CursorParams(after=after, limit=limit)
    item_service = ItemService()
    result = item_service.get_items_paginated(db, cursor_params)
    
    # Convert SQLAlchemy models to Pydantic models
    items = [ItemRead.from_orm(item) for item in result.items]
    
    # Create pagination metadata
    pagination_meta = PaginationMeta(
        per_page=limit,
        next_cursor=result.next_cursor,
        has_next=result.next_cursor is not None
    )
    
    return create_paginated_response(
        items=items,
        meta=pagination_meta,
        message="Items retrieved successfully",
        request_id=request_id
    )


@router.get("/{item_id}", response_model=SuccessResponse[ItemRead])
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    request_id: str = RequestID
) -> SuccessResponse[ItemRead]:
    """
    Get a specific item by ID.
    
    Args:
        item_id: Item ID
        db: Database session
        request_id: Request ID for tracking
    
    Returns:
        Success response with item data
    
    Raises:
        HTTPException: If item not found
    """
    item_service = ItemService()
    item = item_service.get_item(db, item_id)
    
    if not item:
        raise ItemNotFoundException(item_id)
    
    item_read = ItemRead.from_orm(item)
    
    return create_success_response(
        data=item_read,
        message="Item retrieved successfully",
        request_id=request_id
    )


@router.put("/{item_id}", response_model=SuccessResponse[ItemRead])
def update_item(
    item_id: int,
    item_data: ItemUpdate,
    db: Session = Depends(get_db),
    request_id: str = RequestID
) -> SuccessResponse[ItemRead]:
    """
    Update an existing item.
    
    Args:
        item_id: Item ID to update
        item_data: Update data
        db: Database session
        request_id: Request ID for tracking
    
    Returns:
        Success response with updated item
    
    Raises:
        HTTPException: If item not found
    """
    item_service = ItemService()
    item = item_service.update_item(db, item_id, item_data)
    
    if not item:
        raise ItemNotFoundException(item_id)
    
    item_read = ItemRead.from_orm(item)
    
    return create_success_response(
        data=item_read,
        message="Item updated successfully",
        request_id=request_id
    )


@router.delete("/{item_id}", response_model=DeleteResponse)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    request_id: str = RequestID
) -> DeleteResponse:
    """
    Delete an item by ID.
    
    Args:
        item_id: Item ID to delete
        db: Database session
        request_id: Request ID for tracking
    
    Returns:
        Delete response
    
    Raises:
        HTTPException: If item not found
    """
    item_service = ItemService()
    item = item_service.delete_item(db, item_id)
    
    if not item:
        raise ItemNotFoundException(item_id)
    
    return create_delete_response(
        deleted=True,
        deleted_id=item_id,
        message=f"Item {item_id} deleted successfully",
        request_id=request_id
    ) 
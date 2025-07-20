"""
Item service for business logic operations.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.item import Item
from app.utils.crud import CRUDBase
from app.utils.pagination import CursorParams, CursorPage, CursorPagination
from app.api.v1.schemas.item import ItemCreate, ItemUpdate, ItemRead


class ItemService:
    """
    Service class for Item business logic operations.
    
    Handles item creation, retrieval, and cursor-based pagination.
    """
    
    def __init__(self):
        """Initialize the service with CRUD operations."""
        self.crud = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
    
    def create_item(self, db: Session, item_data: ItemCreate) -> Item:
        """
        Create a new item.
        
        Args:
            db: Database session
            item_data: Item creation data
        
        Returns:
            The created item
        """
        return self.crud.create(db, obj_in=item_data)
    
    def get_item(self, db: Session, item_id: int) -> Optional[Item]:
        """
        Get an item by ID.
        
        Args:
            db: Database session
            item_id: Item ID
        
        Returns:
            The item or None if not found
        """
        return self.crud.get(db, id=item_id)
    
    def get_items_paginated(
        self, db: Session, cursor_params: CursorParams
    ) -> CursorPage[Item]:
        """
        Get items with cursor-based pagination.
        
        Args:
            db: Database session
            cursor_params: Pagination parameters
        
        Returns:
            CursorPage with items and next cursor
        """
        query = db.query(Item)
        return CursorPagination.paginate_query(
            query=query,
            cursor_params=cursor_params,
            cursor_field="id",
            order_desc=True
        )
    
    def update_item(
        self, db: Session, item_id: int, item_data: ItemUpdate
    ) -> Optional[Item]:
        """
        Update an existing item.
        
        Args:
            db: Database session
            item_id: Item ID to update
            item_data: Update data
        
        Returns:
            The updated item or None if not found
        """
        db_obj = self.crud.get(db, id=item_id)
        if not db_obj:
            return None
        
        return self.crud.update(db, db_obj=db_obj, obj_in=item_data)
    
    def delete_item(self, db: Session, item_id: int) -> Optional[Item]:
        """
        Delete an item by ID.
        
        Args:
            db: Database session
            item_id: Item ID to delete
        
        Returns:
            The deleted item or None if not found
        """
        db_obj = self.crud.get(db, id=item_id)
        if not db_obj:
            return None
        
        return self.crud.remove(db, id=item_id)
    
    def search_items(
        self, db: Session, name: Optional[str] = None, cursor_params: CursorParams = None
    ) -> CursorPage[Item]:
        """
        Search items by name with pagination.
        
        Args:
            db: Database session
            name: Name to search for (partial match)
            cursor_params: Pagination parameters
        
        Returns:
            CursorPage with matching items
        """
        query = db.query(Item)
        
        if name:
            query = query.filter(Item.name.ilike(f"%{name}%"))
        
        if cursor_params is None:
            cursor_params = CursorParams()
        
        return CursorPagination.paginate_query(
            query=query,
            cursor_params=cursor_params,
            cursor_field="id",
            order_desc=True
        ) 
"""
Cursor-based pagination utilities.
"""
import base64
import json
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, conint
from sqlalchemy.orm import Query
from sqlalchemy import desc, asc

ModelType = TypeVar("ModelType")


class CursorParams(BaseModel):
    """Parameters for cursor-based pagination."""
    
    after: Optional[str] = None
    limit: conint(gt=0, le=100) = 20


class CursorPage(BaseModel, Generic[ModelType]):
    """Cursor-based pagination response."""
    
    items: List[ModelType]
    next_cursor: Optional[str]
    
    class Config:
        arbitrary_types_allowed = True


class CursorPagination:
    """
    Cursor-based pagination helper.
    
    Provides utilities for implementing cursor-based pagination with SQLAlchemy queries.
    """
    
    @staticmethod
    def encode_cursor(data: dict) -> str:
        """
        Encode cursor data to base64 string.
        
        Args:
            data: Dictionary containing cursor data
        
        Returns:
            Base64 encoded cursor string
        """
        json_str = json.dumps(data, sort_keys=True)
        return base64.b64encode(json_str.encode()).decode()
    
    @staticmethod
    def decode_cursor(cursor: str) -> dict:
        """
        Decode cursor string to dictionary.
        
        Args:
            cursor: Base64 encoded cursor string
        
        Returns:
            Decoded cursor data as dictionary
        
        Raises:
            ValueError: If cursor is invalid
        """
        try:
            json_str = base64.b64decode(cursor.encode()).decode()
            return json.loads(json_str)
        except (base64.binascii.Error, json.JSONDecodeError):
            raise ValueError(f"Invalid cursor: {cursor}")
    
    @staticmethod
    def paginate_query(
        query: Query,
        cursor_params: CursorParams,
        cursor_field: str = "id",
        order_desc: bool = True
    ) -> CursorPage:
        """
        Apply cursor pagination to a SQLAlchemy query.
        
        Args:
            query: SQLAlchemy query to paginate
            cursor_params: Pagination parameters
            cursor_field: Field to use for cursor (default: "id")
            order_desc: Whether to order in descending order (default: True)
        
        Returns:
            CursorPage with items and next cursor
        """
        # Get the model class from the query
        model_class = query.column_descriptions[0]['type']
        
        # Apply ordering
        if order_desc:
            query = query.order_by(desc(getattr(model_class, cursor_field)))
        else:
            query = query.order_by(asc(getattr(model_class, cursor_field)))
        
        # Apply cursor filter if provided
        if cursor_params.after:
            try:
                cursor_data = CursorPagination.decode_cursor(cursor_params.after)
                cursor_value = cursor_data.get(cursor_field)
                if cursor_value is not None:
                    if order_desc:
                        query = query.filter(getattr(model_class, cursor_field) < cursor_value)
                    else:
                        query = query.filter(getattr(model_class, cursor_field) > cursor_value)
            except ValueError:
                # If cursor is invalid, return empty result
                return CursorPage(items=[], next_cursor=None)
        
        # Apply limit
        query = query.limit(cursor_params.limit + 1)  # Get one extra to check if there's a next page
        
        # Execute query
        items = query.all()
        
        # Check if there's a next page
        has_next = len(items) > cursor_params.limit
        if has_next:
            items = items[:-1]  # Remove the extra item
        
        # Generate next cursor
        next_cursor = None
        if has_next and items:
            last_item = items[-1]
            cursor_data = {cursor_field: getattr(last_item, cursor_field)}
            next_cursor = CursorPagination.encode_cursor(cursor_data)
        
        return CursorPage(items=items, next_cursor=next_cursor) 
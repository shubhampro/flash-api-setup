"""
Custom exceptions for the application.
"""
from fastapi import HTTPException, status


class ItemNotFoundException(HTTPException):
    """Exception raised when an item is not found."""
    
    def __init__(self, item_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )


class InvalidCursorException(HTTPException):
    """Exception raised when an invalid cursor is provided."""
    
    def __init__(self, cursor: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid cursor: {cursor}"
        )


class ValidationError(HTTPException):
    """Exception raised for validation errors."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        ) 
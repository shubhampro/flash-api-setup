"""
Generic response schemas for standardized API responses.
"""
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

# Type variables for generic responses
DataT = TypeVar("DataT")
ItemT = TypeVar("ItemT")


class ResponseStatus(str, Enum):
    """Response status enumeration."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class ErrorCode(str, Enum):
    """Common error codes."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    CONFLICT = "CONFLICT"
    RATE_LIMITED = "RATE_LIMITED"


class BaseResponse(BaseModel):
    """Base response model with common fields."""
    
    status: ResponseStatus = Field(..., description="Response status")
    message: Optional[str] = Field(None, description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class SuccessResponse(BaseResponse, Generic[DataT]):
    """Generic success response model."""
    
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    data: Optional[DataT] = Field(None, description="Response data")
    meta: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ErrorDetail(BaseModel):
    """Error detail information."""
    
    code: ErrorCode = Field(..., description="Error code")
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    value: Optional[Any] = Field(None, description="Value that caused the error")


class ErrorResponse(BaseResponse):
    """Error response model."""
    
    status: ResponseStatus = Field(default=ResponseStatus.ERROR, description="Response status")
    error_code: ErrorCode = Field(..., description="Error code")
    details: Optional[List[ErrorDetail]] = Field(None, description="Detailed error information")
    debug_info: Optional[Dict[str, Any]] = Field(None, description="Debug information (only in development)")


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    
    page: Optional[int] = Field(None, description="Current page number")
    per_page: Optional[int] = Field(None, description="Items per page")
    total: Optional[int] = Field(None, description="Total number of items")
    total_pages: Optional[int] = Field(None, description="Total number of pages")
    has_next: Optional[bool] = Field(None, description="Whether there's a next page")
    has_prev: Optional[bool] = Field(None, description="Whether there's a previous page")
    next_cursor: Optional[str] = Field(None, description="Next cursor for cursor-based pagination")
    prev_cursor: Optional[str] = Field(None, description="Previous cursor for cursor-based pagination")


class PaginatedResponse(BaseResponse, Generic[ItemT]):
    """Generic paginated response model."""
    
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    data: List[ItemT] = Field(default_factory=list, description="List of items")
    meta: PaginationMeta = Field(..., description="Pagination metadata")


class ListResponse(BaseResponse, Generic[ItemT]):
    """Generic list response model (non-paginated)."""
    
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    data: List[ItemT] = Field(default_factory=list, description="List of items")
    meta: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class DeleteResponse(BaseResponse):
    """Response model for delete operations."""
    
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    deleted: bool = Field(..., description="Whether the item was deleted")
    deleted_id: Optional[Union[int, str]] = Field(None, description="ID of the deleted item")


class HealthCheckResponse(BaseResponse):
    """Health check response model."""
    
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    data: Dict[str, Any] = Field(..., description="Health check data")
    version: str = Field(..., description="API version")
    uptime: Optional[float] = Field(None, description="Application uptime in seconds")


# Convenience functions for creating responses
def create_success_response(
    data: Any = None,
    message: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> SuccessResponse:
    """Create a success response."""
    return SuccessResponse(
        data=data,
        message=message,
        meta=meta,
        request_id=request_id
    )


def create_error_response(
    error_code: ErrorCode,
    message: str,
    details: Optional[List[ErrorDetail]] = None,
    debug_info: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> ErrorResponse:
    """Create an error response."""
    return ErrorResponse(
        error_code=error_code,
        message=message,
        details=details,
        debug_info=debug_info,
        request_id=request_id
    )


def create_paginated_response(
    items: List[Any],
    meta: PaginationMeta,
    message: Optional[str] = None,
    request_id: Optional[str] = None
) -> PaginatedResponse:
    """Create a paginated response."""
    return PaginatedResponse(
        data=items,
        meta=meta,
        message=message,
        request_id=request_id
    )


def create_list_response(
    items: List[Any],
    message: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> ListResponse:
    """Create a list response."""
    return ListResponse(
        data=items,
        message=message,
        meta=meta,
        request_id=request_id
    )


def create_delete_response(
    deleted: bool,
    deleted_id: Optional[Union[int, str]] = None,
    message: Optional[str] = None,
    request_id: Optional[str] = None
) -> DeleteResponse:
    """Create a delete response."""
    return DeleteResponse(
        deleted=deleted,
        deleted_id=deleted_id,
        message=message,
        request_id=request_id
    ) 
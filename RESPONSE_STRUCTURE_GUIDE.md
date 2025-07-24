# Generic Response Structure Guide

This guide explains the standardized response structure implemented across the FastAPI application.

## Overview

The application now uses a consistent response format for all API endpoints, providing:
- Standardized success and error responses
- Request tracking with unique IDs
- Consistent pagination structure
- Proper error handling with detailed information

## Response Structure

### Base Response Fields

All responses include these common fields:

```json
{
  "status": "success|error|warning",
  "message": "Human-readable message",
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "uuid-string-for-tracking"
}
```

### Success Response

```json
{
  "status": "success",
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    // Your actual data here
  },
  "meta": {
    // Optional metadata
  }
}
```

### Error Response

```json
{
  "status": "error",
  "message": "Error description",
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "error_code": "VALIDATION_ERROR",
  "details": [
    {
      "code": "VALIDATION_ERROR",
      "field": "email",
      "message": "Invalid email format",
      "value": "invalid-email"
    }
  ],
  "debug_info": {
    // Debug information (development only)
  }
}
```

### Paginated Response

```json
{
  "status": "success",
  "message": "Items retrieved successfully",
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": [
    // Array of items
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false,
    "next_cursor": "base64-encoded-cursor",
    "prev_cursor": null
  }
}
```

## Available Response Types

### 1. SuccessResponse[DataT]
For single item operations (create, read, update)

```python
from app.api.v1.schemas.response import SuccessResponse, create_success_response

@router.get("/{item_id}", response_model=SuccessResponse[ItemRead])
def get_item(item_id: int, request_id: str = RequestID):
    item = get_item_from_db(item_id)
    return create_success_response(
        data=item,
        message="Item retrieved successfully",
        request_id=request_id
    )
```

### 2. PaginatedResponse[ItemT]
For paginated list operations

```python
from app.api.v1.schemas.response import PaginatedResponse, create_paginated_response, PaginationMeta

@router.get("/", response_model=PaginatedResponse[ItemRead])
def list_items(request_id: str = RequestID):
    items = get_items_from_db()
    pagination_meta = PaginationMeta(
        per_page=20,
        total=100,
        has_next=True,
        next_cursor="cursor-string"
    )
    
    return create_paginated_response(
        items=items,
        meta=pagination_meta,
        message="Items retrieved successfully",
        request_id=request_id
    )
```

### 3. ListResponse[ItemT]
For non-paginated list operations

```python
from app.api.v1.schemas.response import ListResponse, create_list_response

@router.get("/all", response_model=ListResponse[ItemRead])
def get_all_items(request_id: str = RequestID):
    items = get_all_items_from_db()
    return create_list_response(
        items=items,
        message="All items retrieved",
        request_id=request_id
    )
```

### 4. DeleteResponse
For delete operations

```python
from app.api.v1.schemas.response import DeleteResponse, create_delete_response

@router.delete("/{item_id}", response_model=DeleteResponse)
def delete_item(item_id: int, request_id: str = RequestID):
    delete_item_from_db(item_id)
    return create_delete_response(
        deleted=True,
        deleted_id=item_id,
        message=f"Item {item_id} deleted successfully",
        request_id=request_id
    )
```

## Error Codes

The following error codes are available:

- `VALIDATION_ERROR`: Input validation failed
- `NOT_FOUND`: Resource not found
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Access forbidden
- `INTERNAL_ERROR`: Server error
- `BAD_REQUEST`: Invalid request
- `CONFLICT`: Resource conflict
- `RATE_LIMITED`: Rate limit exceeded

## Middleware Features

### Request ID Tracking
Every request gets a unique UUID that's included in:
- Response headers (`X-Request-ID`)
- Response body
- Log messages

### Processing Time
Response headers include `X-Processing-Time` with request duration in milliseconds.

### Automatic Logging
All requests and responses are automatically logged with:
- Request ID
- Method and URL
- Status code
- Processing time
- Client IP

## Usage Examples

### Creating a New Endpoint

```python
from fastapi import APIRouter, Depends
from app.utils.dependencies import RequestID
from app.api.v1.schemas.response import (
    SuccessResponse,
    create_success_response
)

router = APIRouter()

@router.post("/users", response_model=SuccessResponse[UserRead])
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    request_id: str = RequestID
):
    user = user_service.create_user(db, user_data)
    return create_success_response(
        data=UserRead.from_orm(user),
        message="User created successfully",
        request_id=request_id
    )
```

### Error Handling

```python
from app.utils.middleware import create_not_found_error_response

@router.get("/users/{user_id}")
def get_user(user_id: int, request: Request):
    user = user_service.get_user(user_id)
    if not user:
        return create_not_found_error_response(
            resource="User",
            resource_id=str(user_id),
            request_id=get_request_id(request)
        )
    return create_success_response(data=user)
```

### Custom Error Response

```python
from app.api.v1.schemas.response import create_error_response, ErrorCode, ErrorDetail

def custom_error_handler(request_id: str):
    error_details = [
        ErrorDetail(
            code=ErrorCode.VALIDATION_ERROR,
            field="email",
            message="Email already exists",
            value="user@example.com"
        )
    ]
    
    return create_error_response(
        error_code=ErrorCode.CONFLICT,
        message="User creation failed",
        details=error_details,
        request_id=request_id
    )
```

## Migration Guide

### Before (Old Response Format)
```python
@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int):
    item = get_item_from_db(item_id)
    return ItemRead.from_orm(item)
```

### After (New Response Format)
```python
@router.get("/{item_id}", response_model=SuccessResponse[ItemRead])
def get_item(
    item_id: int,
    request_id: str = RequestID
):
    item = get_item_from_db(item_id)
    return create_success_response(
        data=ItemRead.from_orm(item),
        message="Item retrieved successfully",
        request_id=request_id
    )
```

## Benefits

1. **Consistency**: All endpoints return the same response structure
2. **Traceability**: Request IDs enable easy request tracking
3. **Error Handling**: Standardized error responses with detailed information
4. **Monitoring**: Processing time and logging for performance monitoring
5. **Documentation**: Clear response schemas for API consumers
6. **Debugging**: Request IDs and debug information for troubleshooting

## Testing

When testing endpoints, you can now expect consistent response structures:

```python
def test_get_item(client):
    response = client.get("/api/v1/items/1")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert "request_id" in data
    assert "timestamp" in data
    assert "data" in data
    assert data["data"]["id"] == 1
```

## Configuration

The response structure is automatically applied through middleware. No additional configuration is required for basic usage.

For custom error handling or response modification, you can use the provided utility functions in `app.utils.middleware`. 
"""
Tests for generic response structure.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.v1.schemas.response import (
    create_success_response,
    create_error_response,
    create_paginated_response,
    create_delete_response,
    ResponseStatus,
    ErrorCode,
    PaginationMeta
)

client = TestClient(app)


class TestResponseStructure:
    """Test class for response structure."""
    
    def test_root_endpoint_response_structure(self):
        """Test that root endpoint returns proper response structure."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "status" in data
        assert "message" in data
        assert "timestamp" in data
        assert "request_id" in data
        assert "data" in data
        
        # Check values
        assert data["status"] == "success"
        assert data["message"] == "API is running successfully"
        assert "version" in data["data"]
        assert "databases" in data["data"]
    
    def test_health_endpoint_response_structure(self):
        """Test that health endpoint returns proper response structure."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "status" in data
        assert "message" in data
        assert "timestamp" in data
        assert "request_id" in data
        assert "data" in data
        
        # Check values
        assert data["status"] == "success"
        assert data["message"] == "Health check passed"
        assert data["data"]["status"] == "healthy"
    
    def test_request_id_header(self):
        """Test that request ID is included in response headers."""
        response = client.get("/")
        
        assert "X-Request-ID" in response.headers
        request_id = response.headers["X-Request-ID"]
        
        # Check that request ID is a valid UUID format
        import uuid
        try:
            uuid.UUID(request_id)
        except ValueError:
            pytest.fail(f"Request ID {request_id} is not a valid UUID")
    
    def test_processing_time_header(self):
        """Test that processing time is included in response headers."""
        response = client.get("/")
        
        assert "X-Processing-Time" in response.headers
        processing_time = response.headers["X-Processing-Time"]
        
        # Check that processing time is a valid format (number + "ms")
        assert processing_time.endswith("ms")
        try:
            float(processing_time.replace("ms", ""))
        except ValueError:
            pytest.fail(f"Processing time {processing_time} is not a valid number")
    
    def test_create_success_response(self):
        """Test create_success_response function."""
        test_data = {"id": 1, "name": "test"}
        response = create_success_response(
            data=test_data,
            message="Test success",
            request_id="test-request-id"
        )
        
        assert response.status == ResponseStatus.SUCCESS
        assert response.message == "Test success"
        assert response.request_id == "test-request-id"
        assert response.data == test_data
    
    def test_create_error_response(self):
        """Test create_error_response function."""
        response = create_error_response(
            error_code=ErrorCode.NOT_FOUND,
            message="Resource not found",
            request_id="test-request-id"
        )
        
        assert response.status == ResponseStatus.ERROR
        assert response.error_code == ErrorCode.NOT_FOUND
        assert response.message == "Resource not found"
        assert response.request_id == "test-request-id"
    
    def test_create_paginated_response(self):
        """Test create_paginated_response function."""
        items = [{"id": 1}, {"id": 2}]
        meta = PaginationMeta(
            page=1,
            per_page=20,
            total=100,
            has_next=True
        )
        
        response = create_paginated_response(
            items=items,
            meta=meta,
            message="Items retrieved",
            request_id="test-request-id"
        )
        
        assert response.status == ResponseStatus.SUCCESS
        assert response.message == "Items retrieved"
        assert response.request_id == "test-request-id"
        assert response.data == items
        assert response.meta == meta
    
    def test_create_delete_response(self):
        """Test create_delete_response function."""
        response = create_delete_response(
            deleted=True,
            deleted_id=123,
            message="Item deleted",
            request_id="test-request-id"
        )
        
        assert response.status == ResponseStatus.SUCCESS
        assert response.deleted is True
        assert response.deleted_id == 123
        assert response.message == "Item deleted"
        assert response.request_id == "test-request-id"
    
    def test_items_endpoint_response_structure(self):
        """Test that items endpoint returns proper response structure."""
        # First create an item
        create_data = {"name": "Test Item", "description": "Test Description"}
        create_response = client.post("/api/v1/items/", json=create_data)
        
        assert create_response.status_code == 201
        create_data = create_response.json()
        
        # Check response structure
        assert "status" in create_data
        assert "message" in create_data
        assert "timestamp" in create_data
        assert "request_id" in create_data
        assert "data" in create_data
        
        # Get the created item
        item_id = create_data["data"]["id"]
        get_response = client.get(f"/api/v1/items/{item_id}")
        
        assert get_response.status_code == 200
        get_data = get_response.json()
        
        # Check response structure
        assert "status" in get_data
        assert "message" in get_data
        assert "timestamp" in get_data
        assert "request_id" in get_data
        assert "data" in get_data
        assert get_data["data"]["id"] == item_id
    
    def test_items_list_response_structure(self):
        """Test that items list endpoint returns proper paginated response structure."""
        response = client.get("/api/v1/items/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "status" in data
        assert "message" in data
        assert "timestamp" in data
        assert "request_id" in data
        assert "data" in data
        assert "meta" in data
        
        # Check pagination metadata
        assert "per_page" in data["meta"]
        assert "has_next" in data["meta"]
        assert "next_cursor" in data["meta"]
        
        # Check that data is a list
        assert isinstance(data["data"], list) 
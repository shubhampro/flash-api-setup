"""
Tests for items API endpoints.
"""
import pytest
from fastapi import status
from app.services.item_service import ItemService
from app.utils.pagination import CursorParams


class TestItemsAPI:
    """Test class for items API endpoints."""
    
    def test_create_item(self, client, sample_item_data):
        """Test creating a new item."""
        response = client.post("/api/v1/items/", json=sample_item_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["name"] == sample_item_data["name"]
        assert data["description"] == sample_item_data["description"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_item_invalid_data(self, client):
        """Test creating an item with invalid data."""
        invalid_data = {"name": ""}  # Empty name
        response = client.post("/api/v1/items/", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_item(self, client, sample_item_data):
        """Test getting a specific item."""
        # First create an item
        create_response = client.post("/api/v1/items/", json=sample_item_data)
        created_item = create_response.json()
        
        # Then get the item
        response = client.get(f"/api/v1/items/{created_item['id']}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == created_item["id"]
        assert data["name"] == sample_item_data["name"]
        assert data["description"] == sample_item_data["description"]
    
    def test_get_item_not_found(self, client):
        """Test getting a non-existent item."""
        response = client.get("/api/v1/items/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_item(self, client, sample_item_data):
        """Test updating an existing item."""
        # First create an item
        create_response = client.post("/api/v1/items/", json=sample_item_data)
        created_item = create_response.json()
        
        # Update the item
        update_data = {"name": "Updated Item", "description": "Updated description"}
        response = client.put(f"/api/v1/items/{created_item['id']}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["id"] == created_item["id"]
    
    def test_update_item_not_found(self, client):
        """Test updating a non-existent item."""
        update_data = {"name": "Updated Item"}
        response = client.put("/api/v1/items/999", json=update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_item(self, client, sample_item_data):
        """Test deleting an item."""
        # First create an item
        create_response = client.post("/api/v1/items/", json=sample_item_data)
        created_item = create_response.json()
        
        # Delete the item
        response = client.delete(f"/api/v1/items/{created_item['id']}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["id"] == created_item["id"]
        
        # Verify item is deleted
        get_response = client.get(f"/api/v1/items/{created_item['id']}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_item_not_found(self, client):
        """Test deleting a non-existent item."""
        response = client.delete("/api/v1/items/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestItemsPagination:
    """Test class for cursor-based pagination."""
    
    def test_list_items_empty(self, client):
        """Test listing items when database is empty."""
        response = client.get("/api/v1/items/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["items"] == []
        assert data["next_cursor"] is None
    
    def test_list_items_pagination(self, client, sample_items_data):
        """Test cursor-based pagination."""
        # Create multiple items
        for item_data in sample_items_data:
            client.post("/api/v1/items/", json=item_data)
        
        # Test first page (default limit is 20)
        response = client.get("/api/v1/items/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["items"]) == 20  # Default limit
        assert data["next_cursor"] is not None
        
        # Test second page using cursor
        next_cursor = data["next_cursor"]
        response2 = client.get(f"/api/v1/items/?after={next_cursor}")
        
        assert response2.status_code == status.HTTP_200_OK
        data2 = response2.json()
        
        assert len(data2["items"]) == 5  # Remaining items
        assert data2["next_cursor"] is None  # No more pages
    
    def test_list_items_custom_limit(self, client, sample_items_data):
        """Test pagination with custom limit."""
        # Create multiple items
        for item_data in sample_items_data:
            client.post("/api/v1/items/", json=item_data)
        
        # Test with custom limit
        response = client.get("/api/v1/items/?limit=10")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["items"]) == 10
        assert data["next_cursor"] is not None
    
    def test_list_items_invalid_cursor(self, client):
        """Test pagination with invalid cursor."""
        response = client.get("/api/v1/items/?after=invalid_cursor")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should return empty result for invalid cursor
        assert data["items"] == []
        assert data["next_cursor"] is None
    
    def test_list_items_limit_validation(self, client):
        """Test limit validation."""
        # Test limit too high
        response = client.get("/api/v1/items/?limit=101")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test limit too low
        response = client.get("/api/v1/items/?limit=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestItemService:
    """Test class for ItemService business logic."""
    
    def test_create_item_service(self, db_session, sample_item_data):
        """Test item creation through service."""
        from app.api.v1.schemas.item import ItemCreate
        
        item_service = ItemService()
        item_create = ItemCreate(**sample_item_data)
        item = item_service.create_item(db_session, item_create)
        
        assert item.name == sample_item_data["name"]
        assert item.description == sample_item_data["description"]
        assert item.id is not None
    
    def test_get_items_paginated_service(self, db_session, sample_items_data):
        """Test pagination through service."""
        from app.api.v1.schemas.item import ItemCreate
        
        item_service = ItemService()
        
        # Create items
        for item_data in sample_items_data:
            item_create = ItemCreate(**item_data)
            item_service.create_item(db_session, item_create)
        
        # Test pagination
        cursor_params = CursorParams(limit=10)
        result = item_service.get_items_paginated(db_session, cursor_params)
        
        assert len(result.items) == 10
        assert result.next_cursor is not None
        
        # Test second page
        cursor_params2 = CursorParams(after=result.next_cursor, limit=10)
        result2 = item_service.get_items_paginated(db_session, cursor_params2)
        
        assert len(result2.items) == 10
        assert result2.next_cursor is not None 
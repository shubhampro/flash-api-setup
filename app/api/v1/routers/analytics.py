"""
Analytics API endpoints for working with analytics database.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_analytics_db
from app.services.analytics_service import AnalyticsService
from app.services.logging_service import LoggingService
from app.models.analytics import UserActivity, ItemView
from app.models.logs import LogLevel
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class UserActivityCreate(BaseModel):
    """Schema for creating user activity."""
    user_id: int
    action: str
    page_url: Optional[str] = None
    session_duration: Optional[int] = None
    ip_address: Optional[str] = None


class ItemViewCreate(BaseModel):
    """Schema for creating item view."""
    item_id: int
    user_id: Optional[int] = None


class UserActivityResponse(BaseModel):
    """Schema for user activity response."""
    id: int
    user_id: int
    action: str
    page_url: Optional[str]
    session_duration: Optional[int]
    ip_address: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ItemViewResponse(BaseModel):
    """Schema for item view response."""
    id: int
    item_id: int
    user_id: Optional[int]
    view_count: int
    last_viewed_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class PopularItemResponse(BaseModel):
    """Schema for popular item response."""
    item_id: int
    total_views: int
    unique_views: int


@router.post("/user-activity", response_model=UserActivityResponse)
def create_user_activity(
    activity: UserActivityCreate,
    db: Session = Depends(get_analytics_db)
):
    """Create a new user activity log."""
    try:
        # Log to analytics database
        new_activity = AnalyticsService.log_user_activity(
            user_id=activity.user_id,
            action=activity.action,
            page_url=activity.page_url,
            session_duration=activity.session_duration,
            ip_address=activity.ip_address
        )
        
        # Log to logs database
        LoggingService.log_application_event(
            level=LogLevel.INFO,
            message=f"User activity logged: {activity.action}",
            logger_name="analytics",
            module="analytics",
            function="create_user_activity"
        )
        
        return new_activity
    except Exception as e:
        LoggingService.log_exception(e, "analytics", "analytics", "create_user_activity")
        raise HTTPException(status_code=500, detail="Failed to log user activity")


@router.post("/item-view", response_model=ItemViewResponse)
def create_item_view(
    view: ItemViewCreate,
    db: Session = Depends(get_analytics_db)
):
    """Create or update an item view log."""
    try:
        # Log to analytics database
        item_view = AnalyticsService.log_item_view(
            item_id=view.item_id,
            user_id=view.user_id
        )
        
        # Log to logs database
        LoggingService.log_application_event(
            level=LogLevel.INFO,
            message=f"Item view logged: item_id={view.item_id}",
            logger_name="analytics",
            module="analytics",
            function="create_item_view"
        )
        
        return item_view
    except Exception as e:
        LoggingService.log_exception(e, "analytics", "analytics", "create_item_view")
        raise HTTPException(status_code=500, detail="Failed to log item view")


@router.get("/user-activities", response_model=List[UserActivityResponse])
def get_user_activities(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    limit: int = Query(100, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_analytics_db)
):
    """Get user activities with optional filtering."""
    try:
        activities = AnalyticsService.get_user_activities(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        return activities
    except Exception as e:
        LoggingService.log_exception(e, "analytics", "analytics", "get_user_activities")
        raise HTTPException(status_code=500, detail="Failed to retrieve user activities")


@router.get("/item-views", response_model=List[ItemViewResponse])
def get_item_views(
    item_id: Optional[int] = Query(None, description="Filter by item ID"),
    limit: int = Query(100, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_analytics_db)
):
    """Get item views with optional filtering."""
    try:
        views = AnalyticsService.get_item_views(
            item_id=item_id,
            limit=limit,
            offset=offset
        )
        return views
    except Exception as e:
        LoggingService.log_exception(e, "analytics", "analytics", "get_item_views")
        raise HTTPException(status_code=500, detail="Failed to retrieve item views")


@router.get("/popular-items", response_model=List[PopularItemResponse])
def get_popular_items(
    limit: int = Query(10, le=100, description="Number of popular items to return"),
    db: Session = Depends(get_analytics_db)
):
    """Get most viewed items."""
    try:
        popular_items = AnalyticsService.get_popular_items(limit=limit)
        return popular_items
    except Exception as e:
        LoggingService.log_exception(e, "analytics", "analytics", "get_popular_items")
        raise HTTPException(status_code=500, detail="Failed to retrieve popular items")


@router.get("/stats/summary")
def get_analytics_summary(db: Session = Depends(get_analytics_db)):
    """Get analytics summary statistics."""
    try:
        # Get total user activities
        total_activities = len(AnalyticsService.get_user_activities(limit=1000000))
        
        # Get total item views
        total_views = len(AnalyticsService.get_item_views(limit=1000000))
        
        # Get popular items
        popular_items = AnalyticsService.get_popular_items(limit=5)
        
        return {
            "total_user_activities": total_activities,
            "total_item_views": total_views,
            "top_popular_items": popular_items
        }
    except Exception as e:
        LoggingService.log_exception(e, "analytics", "analytics", "get_analytics_summary")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics summary") 
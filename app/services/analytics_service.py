"""
Analytics service for working with analytics database.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from app.models.analytics import UserActivity, ItemView
from app.db.session import get_analytics_db
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics database operations."""
    
    @staticmethod
    def log_user_activity(
        user_id: int,
        action: str,
        page_url: Optional[str] = None,
        session_duration: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> UserActivity:
        """Log user activity to analytics database."""
        with next(get_analytics_db()) as db:
            activity = UserActivity(
                user_id=user_id,
                action=action,
                page_url=page_url,
                session_duration=session_duration,
                ip_address=ip_address
            )
            db.add(activity)
            db.commit()
            db.refresh(activity)
            logger.info(f"Logged user activity: {action} for user {user_id}")
            return activity
    
    @staticmethod
    def log_item_view(item_id: int, user_id: Optional[int] = None) -> ItemView:
        """Log item view to analytics database."""
        with next(get_analytics_db()) as db:
            # Check if view already exists for this item
            existing_view = db.query(ItemView).filter(
                ItemView.item_id == item_id,
                ItemView.user_id == user_id
            ).first()
            
            if existing_view:
                # Update existing view
                existing_view.view_count += 1
                existing_view.last_viewed_at = func.now()
                db.commit()
                db.refresh(existing_view)
                logger.info(f"Updated item view count for item {item_id}")
                return existing_view
            else:
                # Create new view
                item_view = ItemView(
                    item_id=item_id,
                    user_id=user_id,
                    view_count=1,
                    last_viewed_at=func.now()
                )
                db.add(item_view)
                db.commit()
                db.refresh(item_view)
                logger.info(f"Created new item view for item {item_id}")
                return item_view
    
    @staticmethod
    def get_user_activities(
        user_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[UserActivity]:
        """Get user activities with optional filtering."""
        with next(get_analytics_db()) as db:
            query = db.query(UserActivity)
            
            if user_id:
                query = query.filter(UserActivity.user_id == user_id)
            
            activities = query.order_by(desc(UserActivity.created_at)).offset(offset).limit(limit).all()
            return activities
    
    @staticmethod
    def get_item_views(
        item_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ItemView]:
        """Get item views with optional filtering."""
        with next(get_analytics_db()) as db:
            query = db.query(ItemView)
            
            if item_id:
                query = query.filter(ItemView.item_id == item_id)
            
            views = query.order_by(desc(ItemView.last_viewed_at)).offset(offset).limit(limit).all()
            return views
    
    @staticmethod
    def get_popular_items(limit: int = 10) -> List[dict]:
        """Get most viewed items."""
        with next(get_analytics_db()) as db:
            popular_items = db.query(
                ItemView.item_id,
                func.sum(ItemView.view_count).label('total_views'),
                func.count(ItemView.id).label('unique_views')
            ).group_by(ItemView.item_id).order_by(
                desc(func.sum(ItemView.view_count))
            ).limit(limit).all()
            
            return [
                {
                    "item_id": item.item_id,
                    "total_views": item.total_views,
                    "unique_views": item.unique_views
                }
                for item in popular_items
            ] 
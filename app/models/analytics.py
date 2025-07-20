"""
Analytics models for analytics database.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import AnalyticsBaseModel


class UserActivity(AnalyticsBaseModel):
    """User activity tracking for analytics."""
    
    __tablename__ = "user_activities"
    
    user_id = Column(Integer, nullable=False, index=True)
    action = Column(String(100), nullable=False)
    page_url = Column(String(500), nullable=True)
    session_duration = Column(Integer, nullable=True)  # in seconds
    ip_address = Column(String(45), nullable=True)
    
    def __repr__(self):
        return f"<UserActivity(id={self.id}, user_id={self.user_id}, action='{self.action}')>"


class ItemView(AnalyticsBaseModel):
    """Item view analytics."""
    
    __tablename__ = "item_views"
    
    item_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    view_count = Column(Integer, default=1)
    last_viewed_at = Column(DateTime(timezone=True), nullable=False)
    
    def __repr__(self):
        return f"<ItemView(id={self.id}, item_id={self.item_id}, view_count={self.view_count})>" 
"""
Item model for main database.
"""
from sqlalchemy import Column, String, Text, Boolean
from app.db.base import BaseModel


class Item(BaseModel):
    """Item model for main application database."""
    
    __tablename__ = "items"
    
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Item(id={self.id}, title='{self.title}')>" 
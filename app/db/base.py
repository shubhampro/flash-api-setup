"""
SQLAlchemy Base classes for multiple databases.
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func

# Create separate base classes for different databases
Base = declarative_base()
AnalyticsBase = declarative_base()
LogsBase = declarative_base()


class BaseModel(Base):
    """Abstract base model with common fields for main database."""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AnalyticsBaseModel(AnalyticsBase):
    """Abstract base model with common fields for analytics database."""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LogsBaseModel(LogsBase):
    """Abstract base model with common fields for logs database."""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Database metadata for migrations
def get_metadata(database_type: str = "main"):
    """Get metadata for specified database type."""
    if database_type == "main":
        return Base.metadata
    elif database_type == "analytics":
        return AnalyticsBase.metadata
    elif database_type == "logs":
        return LogsBase.metadata
    else:
        raise ValueError(f"Unknown database type: {database_type}") 
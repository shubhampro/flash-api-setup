"""
Multi-database session management for MySQL connections.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Dict, Generator
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Dictionary to store database engines
_engines: Dict[str, any] = {}
_session_factories: Dict[str, sessionmaker] = {}


def get_engine(database_type: str = "main"):
    """Get or create database engine for specified database type."""
    if database_type not in _engines:
        try:
            database_url = settings.get_mysql_url(database_type)
            engine = create_engine(
                database_url,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_recycle=settings.DB_POOL_RECYCLE,
                pool_pre_ping=True,
                echo=False,  # Set to True for SQL query logging
                # MySQL specific settings
                connect_args={
                    "charset": "utf8mb4",
                    "autocommit": False
                }
            )
            _engines[database_type] = engine
            logger.info(f"Created engine for database: {database_type}")
        except Exception as e:
            logger.error(f"Failed to create engine for {database_type}: {str(e)}")
            raise
    
    return _engines[database_type]


def get_session_factory(database_type: str = "main") -> sessionmaker:
    """Get or create session factory for specified database type."""
    if database_type not in _session_factories:
        engine = get_engine(database_type)
        session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        _session_factories[database_type] = session_factory
        logger.info(f"Created session factory for database: {database_type}")
    
    return _session_factories[database_type]


def get_db(database_type: str = "main") -> Generator[Session, None, None]:
    """Dependency to get database session for specified database type."""
    session_factory = get_session_factory(database_type)
    db = session_factory()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error for {database_type}: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


# Convenience functions for different database types
def get_main_db() -> Generator[Session, None, None]:
    """Get main database session."""
    return get_db("main")


def get_analytics_db() -> Generator[Session, None, None]:
    """Get analytics database session."""
    return get_db("analytics")


def get_logs_db() -> Generator[Session, None, None]:
    """Get logs database session."""
    return get_db("logs")


# Legacy support for backward compatibility
def get_db_legacy() -> Generator[Session, None, None]:
    """Legacy function for backward compatibility."""
    return get_main_db()


# Initialize engines on module import
def initialize_engines():
    """Initialize all database engines."""
    try:
        # Initialize main database
        get_engine("main")
        get_engine("analytics")
        get_engine("logs")
        logger.info("All database engines initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database engines: {str(e)}")
        raise


# Call initialization
initialize_engines() 
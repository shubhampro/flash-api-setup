"""
Database initialization script for multiple databases.
"""
from sqlalchemy.orm import Session
from app.db.session import get_engine
from app.db.base import Base, AnalyticsBase, LogsBase
from app.models import Item, UserActivity, ItemView, ApplicationLog, APILog
import logging

logger = logging.getLogger(__name__)


def init_main_database():
    """Initialize main database tables."""
    try:
        engine = get_engine("main")
        Base.metadata.create_all(bind=engine)
        logger.info("Main database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create main database tables: {str(e)}")
        raise


def init_analytics_database():
    """Initialize analytics database tables."""
    try:
        engine = get_engine("analytics")
        AnalyticsBase.metadata.create_all(bind=engine)
        logger.info("Analytics database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create analytics database tables: {str(e)}")
        raise


def init_logs_database():
    """Initialize logs database tables."""
    try:
        engine = get_engine("logs")
        LogsBase.metadata.create_all(bind=engine)
        logger.info("Logs database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create logs database tables: {str(e)}")
        raise


def init_all_databases():
    """Initialize all databases."""
    logger.info("Starting database initialization...")
    
    try:
        init_main_database()
        init_analytics_database()
        init_logs_database()
        logger.info("All databases initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


def create_sample_data():
    """Create sample data for testing."""
    from app.db.session import get_main_db, get_analytics_db, get_logs_db
    
    # Sample data for main database
    with next(get_main_db()) as db:
        sample_item = Item(
            title="Sample Item",
            description="This is a sample item for testing",
            is_active=True
        )
        db.add(sample_item)
        db.commit()
        logger.info("Sample item created in main database")
    
    # Sample data for analytics database
    with next(get_analytics_db()) as db:
        sample_activity = UserActivity(
            user_id=1,
            action="view_item",
            page_url="/api/v1/items/1",
            session_duration=300,
            ip_address="127.0.0.1"
        )
        db.add(sample_activity)
        db.commit()
        logger.info("Sample activity created in analytics database")
    
    # Sample data for logs database
    with next(get_logs_db()) as db:
        sample_log = ApplicationLog(
            level="INFO",
            logger_name="app.main",
            message="Application started successfully",
            module="main",
            function="startup"
        )
        db.add(sample_log)
        db.commit()
        logger.info("Sample log created in logs database")


if __name__ == "__main__":
    # Initialize all databases
    init_all_databases()
    
    # Create sample data
    try:
        create_sample_data()
    except Exception as e:
        logger.warning(f"Could not create sample data: {str(e)}")
        logger.info("Sample data creation skipped. Tables are ready for use.") 
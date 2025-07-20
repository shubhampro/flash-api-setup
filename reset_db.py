#!/usr/bin/env python3
"""
Database reset script to drop and recreate all tables.
"""
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.db.session import get_engine
from app.db.base import Base, AnalyticsBase, LogsBase
from app.models import Item, UserActivity, ItemView, ApplicationLog, APILog
import logging

logger = logging.getLogger(__name__)


def reset_main_database():
    """Reset main database tables."""
    try:
        engine = get_engine("main")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        logger.info("Main database tables reset successfully")
    except Exception as e:
        logger.error(f"Failed to reset main database tables: {str(e)}")
        raise


def reset_analytics_database():
    """Reset analytics database tables."""
    try:
        engine = get_engine("analytics")
        AnalyticsBase.metadata.drop_all(bind=engine)
        AnalyticsBase.metadata.create_all(bind=engine)
        logger.info("Analytics database tables reset successfully")
    except Exception as e:
        logger.error(f"Failed to reset analytics database tables: {str(e)}")
        raise


def reset_logs_database():
    """Reset logs database tables."""
    try:
        engine = get_engine("logs")
        LogsBase.metadata.drop_all(bind=engine)
        LogsBase.metadata.create_all(bind=engine)
        logger.info("Logs database tables reset successfully")
    except Exception as e:
        logger.error(f"Failed to reset logs database tables: {str(e)}")
        raise


def reset_all_databases():
    """Reset all databases."""
    logger.info("Starting database reset...")
    
    try:
        reset_main_database()
        reset_analytics_database()
        reset_logs_database()
        logger.info("All databases reset successfully")
    except Exception as e:
        logger.error(f"Database reset failed: {str(e)}")
        raise


if __name__ == "__main__":
    # Reset all databases
    reset_all_databases() 
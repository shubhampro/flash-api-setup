#!/usr/bin/env python3
"""
Test script to verify all database connections are working.
"""
import sys
import os
from sqlalchemy import text

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.db.session import get_engine, get_main_db, get_analytics_db, get_logs_db
from app.core.config import settings
from app.utils.logger import logger


def test_database_connection(database_type: str):
    """Test connection to a specific database."""
    try:
        engine = get_engine(database_type)
        
        # Test connection with a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            
            if row and row.test == 1:
                logger.info(f"✅ {database_type.upper()} database connection successful")
                return True
            else:
                logger.error(f"❌ {database_type.upper()} database connection failed - unexpected result")
                return False
                
    except Exception as e:
        logger.error(f"❌ {database_type.upper()} database connection failed: {str(e)}")
        return False


def test_session_operations(database_type: str):
    """Test session operations for a specific database."""
    try:
        if database_type == "main":
            with next(get_main_db()) as db:
                result = db.execute(text("SELECT 1 as test"))
                row = result.fetchone()
                if row and row.test == 1:
                    logger.info(f"✅ {database_type.upper()} session operations successful")
                    return True
        elif database_type == "analytics":
            with next(get_analytics_db()) as db:
                result = db.execute(text("SELECT 1 as test"))
                row = result.fetchone()
                if row and row.test == 1:
                    logger.info(f"✅ {database_type.upper()} session operations successful")
                    return True
        elif database_type == "logs":
            with next(get_logs_db()) as db:
                result = db.execute(text("SELECT 1 as test"))
                row = result.fetchone()
                if row and row.test == 1:
                    logger.info(f"✅ {database_type.upper()} session operations successful")
                    return True
                    
        logger.error(f"❌ {database_type.upper()} session operations failed")
        return False
        
    except Exception as e:
        logger.error(f"❌ {database_type.upper()} session operations failed: {str(e)}")
        return False


def main():
    """Main test function."""
    logger.info("🔍 Testing database connections...")
    
    # Test all database connections
    databases = ["main", "analytics", "logs"]
    connection_results = []
    session_results = []
    
    for db_type in databases:
        logger.info(f"\n--- Testing {db_type.upper()} Database ---")
        
        # Test connection
        conn_result = test_database_connection(db_type)
        connection_results.append(conn_result)
        
        # Test session operations
        session_result = test_session_operations(db_type)
        session_results.append(session_result)
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("📊 CONNECTION TEST SUMMARY")
    logger.info("="*50)
    
    for i, db_type in enumerate(databases):
        conn_status = "✅ PASS" if connection_results[i] else "❌ FAIL"
        session_status = "✅ PASS" if session_results[i] else "❌ FAIL"
        logger.info(f"{db_type.upper():12} | Connection: {conn_status} | Session: {session_status}")
    
    # Overall result
    all_passed = all(connection_results) and all(session_results)
    
    if all_passed:
        logger.info("\n🎉 All database connections and operations successful!")
        logger.info("🚀 Your multi-database setup is ready to use!")
        return 0
    else:
        logger.error("\n💥 Some database tests failed!")
        logger.error("🔧 Please check your configuration and MySQL setup.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
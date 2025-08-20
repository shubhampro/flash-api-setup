#!/usr/bin/env python3
"""
Database initialization script
Creates tables and adds initial data
"""

import asyncio
from sqlalchemy import text
from shared.db.base import engine, Base
from shared.db.models.user import User
from shared.core.security import get_password_hash

def init_db():
    """Initialize database with tables and initial data."""
    print("Creating database tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database tables created successfully!")
    
    # Add initial admin user
    create_initial_admin()
    
    print("Database initialization completed!")

def create_initial_admin():
    """Create initial admin user."""
    from shared.db.session import get_db_session
    
    db = get_db_session()
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
        
        if not existing_admin:
            admin_user = User(
                email="admin@example.com",
                username="admin",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True
            )
            
            db.add(admin_user)
            db.commit()
            print("Initial admin user created: admin@example.com / admin123")
        else:
            print("Admin user already exists")
            
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()

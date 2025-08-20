from sqlalchemy.orm import Session
from shared.db.base import SessionLocal

def get_db_session() -> Session:
    """Get database session."""
    return SessionLocal()

def close_db_session(db: Session):
    """Close database session."""
    db.close()

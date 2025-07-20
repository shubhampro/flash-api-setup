"""
Log models for logs database.
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, Enum
from app.db.base import LogsBaseModel
import enum


class LogLevel(enum.Enum):
    """Log levels enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ApplicationLog(LogsBaseModel):
    """Application logs for audit and debugging."""
    
    __tablename__ = "application_logs"
    
    level = Column(Enum(LogLevel), nullable=False, index=True)
    logger_name = Column(String(100), nullable=False, index=True)
    message = Column(Text, nullable=False)
    module = Column(String(100), nullable=True)
    function = Column(String(100), nullable=True)
    line_number = Column(Integer, nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<ApplicationLog(id={self.id}, level={self.level}, message='{self.message[:50]}...')>"


class APILog(LogsBaseModel):
    """API request/response logs."""
    
    __tablename__ = "api_logs"
    
    method = Column(String(10), nullable=False, index=True)
    endpoint = Column(String(500), nullable=False, index=True)
    status_code = Column(Integer, nullable=False, index=True)
    response_time = Column(Integer, nullable=True)  # in milliseconds
    user_id = Column(Integer, nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_body = Column(Text, nullable=True)
    response_body = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<APILog(id={self.id}, method={self.method}, endpoint='{self.endpoint}', status={self.status_code})>" 
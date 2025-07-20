"""
Logging service for working with logs database.
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.models.logs import ApplicationLog, APILog, LogLevel
from app.db.session import get_logs_db
import logging
import traceback
import sys

logger = logging.getLogger(__name__)


class LoggingService:
    """Service for logs database operations."""
    
    @staticmethod
    def log_application_event(
        level: LogLevel,
        message: str,
        logger_name: str = "app",
        module: Optional[str] = None,
        function: Optional[str] = None,
        line_number: Optional[int] = None,
        stack_trace: Optional[str] = None
    ) -> ApplicationLog:
        """Log application event to logs database."""
        with next(get_logs_db()) as db:
            app_log = ApplicationLog(
                level=level,
                logger_name=logger_name,
                message=message,
                module=module,
                function=function,
                line_number=line_number,
                stack_trace=stack_trace
            )
            db.add(app_log)
            db.commit()
            db.refresh(app_log)
            logger.info(f"Logged application event: {level.value} - {message}")
            return app_log
    
    @staticmethod
    def log_api_request(
        method: str,
        endpoint: str,
        status_code: int,
        response_time: Optional[int] = None,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_body: Optional[str] = None,
        response_body: Optional[str] = None
    ) -> APILog:
        """Log API request/response to logs database."""
        with next(get_logs_db()) as db:
            api_log = APILog(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                response_time=response_time,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                request_body=request_body,
                response_body=response_body
            )
            db.add(api_log)
            db.commit()
            db.refresh(api_log)
            logger.info(f"Logged API request: {method} {endpoint} - {status_code}")
            return api_log
    
    @staticmethod
    def log_exception(
        exception: Exception,
        logger_name: str = "app",
        module: Optional[str] = None,
        function: Optional[str] = None
    ) -> ApplicationLog:
        """Log exception with stack trace to logs database."""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        stack_trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        return LoggingService.log_application_event(
            level=LogLevel.ERROR,
            message=str(exception),
            logger_name=logger_name,
            module=module,
            function=function,
            stack_trace=stack_trace
        )
    
    @staticmethod
    def get_application_logs(
        level: Optional[LogLevel] = None,
        logger_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ApplicationLog]:
        """Get application logs with optional filtering."""
        with next(get_logs_db()) as db:
            query = db.query(ApplicationLog)
            
            if level:
                query = query.filter(ApplicationLog.level == level)
            
            if logger_name:
                query = query.filter(ApplicationLog.logger_name == logger_name)
            
            logs = query.order_by(desc(ApplicationLog.created_at)).offset(offset).limit(limit).all()
            return logs
    
    @staticmethod
    def get_api_logs(
        method: Optional[str] = None,
        status_code: Optional[int] = None,
        user_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[APILog]:
        """Get API logs with optional filtering."""
        with next(get_logs_db()) as db:
            query = db.query(APILog)
            
            if method:
                query = query.filter(APILog.method == method)
            
            if status_code:
                query = query.filter(APILog.status_code == status_code)
            
            if user_id:
                query = query.filter(APILog.user_id == user_id)
            
            logs = query.order_by(desc(APILog.created_at)).offset(offset).limit(limit).all()
            return logs
    
    @staticmethod
    def get_error_logs(limit: int = 100) -> List[ApplicationLog]:
        """Get error and critical logs."""
        with next(get_logs_db()) as db:
            error_logs = db.query(ApplicationLog).filter(
                ApplicationLog.level.in_([LogLevel.ERROR, LogLevel.CRITICAL])
            ).order_by(desc(ApplicationLog.created_at)).limit(limit).all()
            return error_logs
    
    @staticmethod
    def get_slow_api_requests(threshold_ms: int = 1000, limit: int = 50) -> List[APILog]:
        """Get API requests that took longer than threshold."""
        with next(get_logs_db()) as db:
            slow_requests = db.query(APILog).filter(
                APILog.response_time > threshold_ms
            ).order_by(desc(APILog.response_time)).limit(limit).all()
            return slow_requests 
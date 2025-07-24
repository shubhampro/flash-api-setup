"""
Middleware for request/response processing.
"""
import time
import uuid
from typing import Callable, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import logger
from app.utils.request_utils import get_request_id
from app.api.v1.schemas.response import (
    create_error_response,
    ErrorCode,
    ErrorDetail
)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to all requests."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add request ID to request state."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add request ID to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class ResponseProcessingMiddleware(BaseHTTPMiddleware):
    """Middleware to process and standardize responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and standardize response format."""
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Add processing time header
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            response.headers["X-Processing-Time"] = f"{processing_time:.2f}ms"
            
            return response
            
        except Exception as e:
            # Log the exception
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            
            # Create standardized error response
            error_response = create_error_response(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Internal server error",
                request_id=getattr(request.state, 'request_id', None)
            )
            
            return JSONResponse(
                status_code=500,
                content=error_response.model_dump()
            )


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response information."""
        start_time = time.time()
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Log request
        logger.info(
            f"Request started - ID: {request_id}, "
            f"Method: {request.method}, "
            f"URL: {request.url}, "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            response = await call_next(request)
            processing_time = (time.time() - start_time) * 1000
            
            # Log response
            logger.info(
                f"Request completed - ID: {request_id}, "
                f"Status: {response.status_code}, "
                f"Time: {processing_time:.2f}ms"
            )
            
            return response
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            
            # Log error
            logger.error(
                f"Request failed - ID: {request_id}, "
                f"Error: {str(e)}, "
                f"Time: {processing_time:.2f}ms",
                exc_info=True
            )
            
            raise


def create_validation_error_response(
    errors: list,
    request_id: Optional[str] = None
) -> JSONResponse:
    """Create standardized validation error response."""
    error_details = []
    
    for error in errors:
        error_detail = ErrorDetail(
            code=ErrorCode.VALIDATION_ERROR,
            field=error.get('loc', [None])[-1] if error.get('loc') else None,
            message=error.get('msg', 'Validation error'),
            value=error.get('input')
        )
        error_details.append(error_detail)
    
    error_response = create_error_response(
        error_code=ErrorCode.VALIDATION_ERROR,
        message="Validation error",
        details=error_details,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=422,
        content=error_response.model_dump()
    )


def create_not_found_error_response(
    resource: str,
    resource_id: str,
    request_id: Optional[str] = None
) -> JSONResponse:
    """Create standardized not found error response."""
    error_response = create_error_response(
        error_code=ErrorCode.NOT_FOUND,
        message=f"{resource} with ID {resource_id} not found",
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=404,
        content=error_response.model_dump()
    )


def create_unauthorized_error_response(
    message: str = "Unauthorized access",
    request_id: Optional[str] = None
) -> JSONResponse:
    """Create standardized unauthorized error response."""
    error_response = create_error_response(
        error_code=ErrorCode.UNAUTHORIZED,
        message=message,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=401,
        content=error_response.model_dump()
    )


def create_forbidden_error_response(
    message: str = "Access forbidden",
    request_id: Optional[str] = None
) -> JSONResponse:
    """Create standardized forbidden error response."""
    error_response = create_error_response(
        error_code=ErrorCode.FORBIDDEN,
        message=message,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=403,
        content=error_response.model_dump()
    ) 
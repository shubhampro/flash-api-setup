"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.version import API_VERSION
from app.api.v1 import api_router
from app.utils.logger import logger
from app.utils.middleware import (
    RequestIDMiddleware,
    ResponseProcessingMiddleware,
    LoggingMiddleware
)
from app.api.v1.schemas.response import (
    create_success_response,
    HealthCheckResponse
)

# Create FastAPI app instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=API_VERSION,
    description="A production-ready FastAPI application with multiple MySQL databases",
    openapi_url=f"/api/{API_VERSION}/openapi.json",
    docs_url=f"/api/{API_VERSION}/docs",
    redoc_url=f"/api/{API_VERSION}/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(ResponseProcessingMiddleware)
app.add_middleware(RequestIDMiddleware)


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Starting FastAPI application with multiple MySQL databases...")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down FastAPI application...")


@app.get("/")
async def root():
    """Root endpoint."""
    return create_success_response(
        data={
            "message": "Welcome to FastAPI Production App with Multiple MySQL Databases",
            "version": API_VERSION,
            "docs": f"/api/{API_VERSION}/docs",
            "databases": ["main", "analytics", "logs"]
        },
        message="API is running successfully"
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return create_success_response(
        data={
            "status": "healthy",
            "version": API_VERSION,
            "databases": ["main", "analytics", "logs"]
        },
        message="Health check passed"
    )


# Include API routers
app.include_router(api_router, prefix=f"/api/{API_VERSION}") 
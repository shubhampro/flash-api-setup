"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.version import API_VERSION
from app.api.v1 import api_router
from app.utils.logger import logger

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
    return {
        "message": "Welcome to FastAPI Production App with Multiple MySQL Databases",
        "version": API_VERSION,
        "docs": f"/api/{API_VERSION}/docs",
        "databases": ["main", "analytics", "logs"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": API_VERSION}


# Include API routers
app.include_router(api_router, prefix=f"/api/{API_VERSION}") 
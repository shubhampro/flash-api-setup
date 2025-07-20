"""
API v1 routes and schemas.
"""
from fastapi import APIRouter
from .routers import items, analytics

api_router = APIRouter()

# Include routers
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"]) 
"""
Common dependencies for API endpoints.
"""
from typing import Optional
from fastapi import Request, Depends
from app.utils.request_utils import get_request_id


def get_request_id_dependency(request: Request) -> str:
    """Dependency to get request ID from request state."""
    return get_request_id(request)


# Common dependency for request ID
RequestID = Depends(get_request_id_dependency) 
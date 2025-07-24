"""
Request utility functions.
"""
from fastapi import Request


def get_request_id(request: Request) -> str:
    """Get request ID from request state."""
    return getattr(request.state, 'request_id', 'unknown') 
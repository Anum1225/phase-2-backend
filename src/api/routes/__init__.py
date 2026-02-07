"""
API route handlers.

This module exports all API routers for registration in the main application.
"""

from .auth import router as auth_router
from .tasks import router as tasks_router

__all__ = [
    "auth_router",
    "tasks_router",
]

"""
Route organization and configuration.

This module imports and configures all API routers with their prefixes.
"""

from fastapi import APIRouter
from api.health import router as health_router
from api.example import router as example_router
from api.importer import router as importer_router

# Create the main API router
api_router = APIRouter()

# Include all feature routers with their prefixes
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(example_router, prefix="/example", tags=["example"])
api_router.include_router(importer_router, prefix="/importer", tags=["importer"])

# Add more routers here as needed:
# api_router.include_router(users_router, prefix="/users", tags=["users"])
# api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

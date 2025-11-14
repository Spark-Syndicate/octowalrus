"""
Example endpoints module.

This module demonstrates how to organize routes by feature or resource.
You can create multiple endpoint files for different features.
"""

from fastapi import APIRouter, Depends
from services.example_service import ExampleService

router = APIRouter()


def get_example_service() -> ExampleService:
    """Dependency injection for the example service."""
    return ExampleService()


@router.get("/info")
async def get_info(service: ExampleService = Depends(get_example_service)):
    """Get service information."""
    return await service.get_service_info()


@router.post("/process")
async def process_data(
    data: dict, service: ExampleService = Depends(get_example_service)
):
    """Process data using the example service."""
    return await service.process_data(data)

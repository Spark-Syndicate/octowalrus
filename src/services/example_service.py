"""
Example service module.

This module demonstrates how to organize business logic in the services directory.
Services handle the core business logic and can be used by multiple routes.
"""

class ExampleService:
    """Example service class for demonstration purposes."""
    
    def __init__(self):
        self.service_name = "octowalrus"
    
    async def get_service_info(self) -> dict:
        """Get information about the service."""
        return {
            "service": self.service_name,
            "status": "operational",
            "version": "0.1.0"
        }
    
    async def process_data(self, data: dict) -> dict:
        """Process some data (example business logic)."""
        # Add your business logic here
        processed_data = {
            "original": data,
            "processed": True,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        return processed_data 
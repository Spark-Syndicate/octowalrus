"""
Tests for example endpoints.

This module contains tests for the example API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from api.example import router
from services.example_service import ExampleService

# Create a test client
client = TestClient(router)


@pytest.mark.asyncio
async def test_get_info_success():
    """Test successful get_info endpoint."""
    with patch("api.example.ExampleService") as mock_service_class:
        mock_service = AsyncMock(spec=ExampleService)
        mock_service.get_service_info.return_value = {
            "service": "test-service",
            "status": "operational",
            "version": "0.1.0",
        }
        mock_service_class.return_value = mock_service

        response = client.get("/info")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "test-service"
        assert data["status"] == "operational"
        assert data["version"] == "0.1.0"
        mock_service.get_service_info.assert_called_once()


@pytest.mark.asyncio
async def test_process_data_success():
    """Test successful process_data endpoint."""
    test_data = {"key": "value"}
    expected_response = {
        "original": test_data,
        "processed": True,
        "timestamp": "2024-01-01T00:00:00Z",
    }

    with patch("api.example.ExampleService") as mock_service_class:
        mock_service = AsyncMock(spec=ExampleService)
        mock_service.process_data.return_value = expected_response
        mock_service_class.return_value = mock_service

        response = client.post("/process", json=test_data)

        assert response.status_code == 200
        data = response.json()
        assert data == expected_response
        mock_service.process_data.assert_called_once_with(test_data)


@pytest.mark.asyncio
async def test_process_data_empty_payload():
    """Test process_data endpoint with empty payload."""
    with patch("api.example.ExampleService") as mock_service_class:
        mock_service = AsyncMock(spec=ExampleService)
        mock_service.process_data.return_value = {
            "original": {},
            "processed": True,
            "timestamp": "2024-01-01T00:00:00Z",
        }
        mock_service_class.return_value = mock_service

        response = client.post("/process", json={})

        assert response.status_code == 200
        data = response.json()
        assert data["original"] == {}
        assert data["processed"] is True

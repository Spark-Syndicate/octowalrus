"""
Tests for health endpoints.

This module contains tests for the health API endpoints.
"""

from fastapi.testclient import TestClient
from api.health import router

# Create a test client
client = TestClient(router)


def test_general_health_success():
    """Test successful general health endpoint."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "octowalrus"

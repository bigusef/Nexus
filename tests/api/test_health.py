"""API tests for health check endpoint."""

import pytest
from httpx import AsyncClient


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    async def test_health_check_returns_200(self, client: AsyncClient):
        """Test health check endpoint returns 200 OK."""
        response = await client.get("/health")

        assert response.status_code == 200

    async def test_health_check_response_structure(self, client: AsyncClient):
        """Test health check response has correct structure."""
        response = await client.get("/health")
        data = response.json()

        assert "status" in data
        assert "environment" in data

    async def test_health_check_status_healthy(self, client: AsyncClient):
        """Test health check returns healthy status."""
        response = await client.get("/health")
        data = response.json()

        assert data["status"] == "healthy"

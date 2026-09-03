"""Tests for SecurityHeadersMiddleware."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
def async_client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestSecurityHeaders:
    async def test_sets_hsts(self, async_client):
        response = await async_client.get("/health")
        assert response.status_code == 200
        assert (
            response.headers["Strict-Transport-Security"] == "max-age=31536000"
        )

    async def test_always_on_security_headers_present(self, async_client):
        response = await async_client.get("/health")
        assert response.status_code == 200
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["Referrer-Policy"] == (
            "strict-origin-when-cross-origin"
        )
        assert (
            response.headers["Permissions-Policy"]
            == "camera=(), microphone=(), geolocation=()"
        )

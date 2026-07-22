"""Integration tests for all API routes."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app

_FAKE_GRAPH_STATE = {
    "iteration": 1,
    "report": {
        "thematic_consistency": "PASS",
        "notes": [],
        "substitutions": [],
        "nutrition_estimate": {"calories_per_serving": 200},
        "validation_issues": [],
    },
    "draft_recipe": {
        "name": "Test Bread",
        "description": "A test recipe",
        "ingredients": [{"item": "flour", "amount": "2 cups", "notes": ""}],
        "instructions": ["Mix", "Bake"],
        "prep_time_minutes": 10,
        "cook_time_minutes": 20,
        "servings": 4,
        "difficulty": "easy",
        "plausibility_notes": [],
    },
}


@pytest.fixture
def async_client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestHealth:
    async def test_returns_healthy(self, async_client):
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestRoot:
    async def test_returns_service_info(self, async_client):
        response = await async_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Guzzlers-n-Dragons"
        assert data["docs"] == "/docs"


class TestIngredients:
    async def test_list_all(self, async_client):
        response = await async_client.get("/alchemy/ingredients")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_filter_by_theme(self, async_client):
        response = await async_client.get(
            "/alchemy/ingredients?thematic_group=high_fantasy"
        )
        assert response.status_code == 200
        data = response.json()
        assert all(i["thematic_group"] == "high_fantasy" for i in data)

    async def test_get_by_name_found(self, async_client):
        response = await async_client.get("/alchemy/ingredients/lembas")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "lembas"

    async def test_get_by_name_not_found(self, async_client):
        response = await async_client.get("/alchemy/ingredients/nonexistent")
        assert response.status_code == 404


class TestTransform:
    async def test_returns_recipe_on_success(self, async_client):
        with patch(
            "src.api.routes.agent_graph.ainvoke",
            AsyncMock(return_value=_FAKE_GRAPH_STATE),
        ):
            response = await async_client.post(
                "/alchemy/transform",
                json={
                    "fictional_ingredient": "lembas",
                    "meal_type": "bread",
                    "thematic_group": "high_fantasy",
                    "constraints": {"servings": 4},
                },
            )
        assert response.status_code == 200
        data = response.json()
        assert data["recipe"]["name"] == "Test Bread"
        assert data["plausibility_report"]["thematic_consistency"] == "PASS"
        assert data["metadata"]["iterations"] == 1

    async def test_returns_422_on_invalid_theme(self, async_client):
        response = await async_client.post(
            "/alchemy/transform",
            json={
                "fictional_ingredient": "lembas",
                "meal_type": "bread",
                "thematic_group": "invalid",
            },
        )
        assert response.status_code == 422

    async def test_returns_422_on_too_many_dietary(self, async_client):
        response = await async_client.post(
            "/alchemy/transform",
            json={
                "fictional_ingredient": "lembas",
                "meal_type": "bread",
                "thematic_group": "high_fantasy",
                "constraints": {"dietary": [str(i) for i in range(21)]},
            },
        )
        assert response.status_code == 422

    async def test_returns_504_on_timeout(self, async_client):
        import asyncio

        async def slow_graph(*args, **kwargs):
            await asyncio.sleep(999)
            return _FAKE_GRAPH_STATE

        with (
            patch("src.api.routes.agent_graph.ainvoke", slow_graph),
            patch("src.api.routes.AGENT_TIMEOUT_SECONDS", 0),
        ):
            response = await async_client.post(
                "/alchemy/transform",
                json={
                    "fictional_ingredient": "lembas",
                    "meal_type": "bread",
                    "thematic_group": "high_fantasy",
                },
            )
            assert response.status_code == 504

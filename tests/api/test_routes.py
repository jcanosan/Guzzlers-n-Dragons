"""Integration tests for all API routes."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.routes import _limit
from src.main import app, rate_limit_handler
from src.schemas.agents import DraftRecipe, PlannerResult


def _parse_sse(text: str) -> list[tuple[str, dict]]:
    events = []
    for raw in text.strip().split("\n\n"):
        if not raw:
            continue
        lines = raw.splitlines()
        name = lines[0].split(": ", 1)[1]
        data = json.loads(lines[1].split(": ", 1)[1])
        events.append((name, data))
    return events


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
    async def test_serves_demo_page(self, async_client):
        response = await async_client.get("/")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        assert "Guzzlers-n-Dragons" in response.text


class TestIngredients:
    async def test_list_all(self, async_client):
        response = await async_client.get("/alchemy/ingredients")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_filter_by_theme(self, async_client):
        response = await async_client.get(
            "/alchemy/ingredients?thematic_group=fantasy"
        )
        assert response.status_code == 200
        data = response.json()
        assert all(i["thematic_group"] == "fantasy" for i in data)

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
                    "thematic_group": "fantasy",
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
                "thematic_group": "fantasy",
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
                    "thematic_group": "fantasy",
                },
            )
            assert response.status_code == 504


class TestTransformStream:
    async def test_streams_node_events(self, async_client):
        async def fake_stream(initial, stream_mode=None):
            yield {"planner": {"iteration": 1, "planner_result": {}}}
            yield {"creator": {"draft_recipe": {"name": "Test Bread"}}}
            yield {"critic": {"report": {"thematic_consistency": "PASS"}}}

        with patch("src.api.routes.agent_graph.astream", fake_stream):
            response = await async_client.post(
                "/alchemy/transform/stream",
                json={
                    "fictional_ingredient": "lembas",
                    "meal_type": "bread",
                    "thematic_group": "fantasy",
                },
            )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        text = response.text
        assert "event: node" in text
        assert "event: done" in text
        assert '"node": "planner"' in text
        assert '"node": "critic"' in text

    async def test_streams_pydantic_payloads(self, async_client):
        async def fake_stream(initial, stream_mode=None):
            yield {
                "planner": {
                    "iteration": 3,
                    "planner_result": PlannerResult(
                        technique_requirements=["roast"]
                    ),
                }
            }
            yield {
                "creator": {"draft_recipe": DraftRecipe(name="Elven Waybread")}
            }
            yield {"critic": {"report": {"thematic_consistency": "PASS"}}}

        with patch("src.api.routes.agent_graph.astream", fake_stream):
            response = await async_client.post(
                "/alchemy/transform/stream",
                json={
                    "fictional_ingredient": "lembas",
                    "meal_type": "bread",
                    "thematic_group": "fantasy",
                },
            )

        assert response.status_code == 200
        events = _parse_sse(response.text)
        planner_event = events[0][1]
        assert planner_event["node"] == "planner"
        assert planner_event["data"]["iteration"] == 3
        assert planner_event["data"]["planner_result"][
            "technique_requirements"
        ] == ["roast"]
        assert events[1][1]["data"]["draft_recipe"]["name"] == (
            "Elven Waybread"
        )
        assert events[2][1]["data"]["report"]["thematic_consistency"] == (
            "PASS"
        )
        assert events[-1] == ("done", {})

    async def test_skips_non_dict_chunks_and_unknown_nodes(self, async_client):
        async def fake_stream(initial, stream_mode=None):
            yield "not a dict"
            yield {"unknown_node": {"foo": "bar"}}
            yield {"planner": {"iteration": 1, "planner_result": {}}}

        with patch("src.api.routes.agent_graph.astream", fake_stream):
            response = await async_client.post(
                "/alchemy/transform/stream",
                json={
                    "fictional_ingredient": "lembas",
                    "meal_type": "bread",
                    "thematic_group": "fantasy",
                },
            )

        events = _parse_sse(response.text)
        assert [name for name, _ in events] == ["node", "done"]
        assert events[0][1]["node"] == "planner"

    async def test_yields_error_event_on_exception(self, async_client):
        async def broken_stream(initial, stream_mode=None):
            raise ValueError("boom")
            yield {}  # makes this an async generator

        with patch("src.api.routes.agent_graph.astream", broken_stream):
            response = await async_client.post(
                "/alchemy/transform/stream",
                json={
                    "fictional_ingredient": "lembas",
                    "meal_type": "bread",
                    "thematic_group": "fantasy",
                },
            )

        assert response.status_code == 200
        events = _parse_sse(response.text)
        assert events == [("error", {"message": "ValueError: boom"})]

    async def test_yields_timeout_error_event(self, async_client):
        async def slow_stream(initial, stream_mode=None):
            await asyncio.sleep(999)
            yield {"planner": {"iteration": 1, "planner_result": {}}}

        with (
            patch("src.api.routes.agent_graph.astream", slow_stream),
            patch("src.api.routes.AGENT_TIMEOUT_SECONDS", 0),
        ):
            response = await async_client.post(
                "/alchemy/transform/stream",
                json={
                    "fictional_ingredient": "lembas",
                    "meal_type": "bread",
                    "thematic_group": "fantasy",
                },
            )

        assert response.status_code == 200
        events = _parse_sse(response.text)
        assert events == [("error", {"message": "Agent pipeline timed out"})]


class TestRateLimit:
    def test_limit_is_noop_when_disabled(self, monkeypatch):
        monkeypatch.setattr("src.api.routes.settings.rate_limit_enabled", False)

        def dummy():
            return "ok"

        assert _limit()(dummy) is dummy

    def test_limit_wraps_when_enabled(self, monkeypatch):
        monkeypatch.setattr("src.api.routes.settings.rate_limit_enabled", True)

        def dummy(request):
            return "ok"

        wrapped = _limit()(dummy)
        assert wrapped is not dummy

    async def test_handler_returns_429(self):
        from slowapi.errors import RateLimitExceeded

        response = await rate_limit_handler(
            MagicMock(),
            RateLimitExceeded(MagicMock(error_message="slow down")),
        )
        assert response.status_code == 429
        assert json.loads(bytes(response.body)) == {
            "detail": "Rate limit exceeded"
        }

"""Tests for agent tools."""

from unittest.mock import AsyncMock, MagicMock, patch

from src.tools.agent_tools import (
    ALL_AGENT_TOOLS,
    find_recipes_by_ingredient,
    get_common_cooking_techniques,
    lookup_ingredient_nutrition,
)


class TestToolRegistry:
    def test_three_tools_registered(self):
        assert len(ALL_AGENT_TOOLS) == 3

    def test_every_tool_has_name(self):
        for tool in ALL_AGENT_TOOLS:
            assert tool.name
            assert isinstance(tool.name, str)

    def test_every_tool_has_description(self):
        for tool in ALL_AGENT_TOOLS:
            assert tool.description
            assert len(tool.description) > 20


class TestLookupIngredientNutrition:
    async def test_fallback_when_all_sources_fail(self):
        with (
            patch("src.services.usda_client.settings.usda_api_key", None),
            patch(
                "src.tools.nutrition.fineli_search_food",
                AsyncMock(return_value=[]),
            ),
            patch(
                "src.tools.nutrition.get_first_nutrition",
                AsyncMock(return_value=None),
            ),
            patch(
                "src.tools.nutrition.get_ingredient_by_name",
                return_value=None,
            ),
        ):
            result = await lookup_ingredient_nutrition.ainvoke(
                {"ingredient_name": "apple"}
            )
            assert result["source"] == "unavailable"


class TestFindRecipesByIngredient:
    async def test_delegates_to_themealdb(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"meals": None}
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        with patch(
            "src.services.themealdb_client.httpx.AsyncClient",
            return_value=mock_client,
        ):
            result = await find_recipes_by_ingredient.ainvoke(
                {"ingredient": "flour"}
            )
            assert isinstance(result, list)


class TestGetCommonCookingTechniques:
    async def test_aggregates_techniques(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"meals": None}
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        with patch(
            "src.services.themealdb_client.httpx.AsyncClient",
            return_value=mock_client,
        ):
            result = await get_common_cooking_techniques.ainvoke(
                {"ingredient": "chicken"}
            )
            assert isinstance(result, list)

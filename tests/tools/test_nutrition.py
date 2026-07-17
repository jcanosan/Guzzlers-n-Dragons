"""Tests for nutrition lookup chain."""

from unittest.mock import AsyncMock, patch

from src.tools.nutrition import lookup_nutrition


class TestLookupNutrition:
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
            result = await lookup_nutrition("apple")
            assert result["source"] == "unavailable"
            assert result["calories_per_serving"] is None

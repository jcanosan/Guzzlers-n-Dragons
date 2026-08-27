"""Tests for nutrition lookup chain."""

from unittest.mock import AsyncMock, patch

from langchain_core.messages import AIMessage
from sqlalchemy.exc import SQLAlchemyError

from src.schemas.domain import FictionalIngredient
from src.tools.nutrition import lookup_nutrition, resolve_approximation


class TestResolveApproximation:
    async def test_prefers_seeded_approximation(self):
        profile = FictionalIngredient(
            name="blue_milk",
            description="",
            thematic_group="sci_fi",
            texture="",
            rarity="common",
            real_world_approximations=[
                {"ingredient": "whole milk", "reasoning": "creamy"}
            ],
        )
        result = await resolve_approximation("blue_milk", profile)
        assert result == "whole milk"

    async def test_llm_fallback_for_unseeded_ingredient(self):
        with patch(
            "src.tools.nutrition.call_llm",
            AsyncMock(return_value=AIMessage(content="cow milk")),
        ):
            result = await resolve_approximation("mutant cow milk", None)
            assert result == "cow milk"

    async def test_llm_fallback_strips_fictional_modifier(self):
        with patch(
            "src.tools.nutrition.call_llm",
            AsyncMock(return_value=AIMessage(content="venison leg")),
        ):
            result = await resolve_approximation("manticore leg", None)
            assert result == "venison leg"

    async def test_falls_back_to_raw_name_on_llm_failure(self):
        with patch(
            "src.tools.nutrition.call_llm",
            AsyncMock(side_effect=RuntimeError("llm down")),
        ):
            result = await resolve_approximation("mutant cow milk", None)
            assert result == "mutant cow milk"


class TestLookupNutrition:
    async def test_fallback_when_all_sources_fail(self):
        with (
            patch("src.services.usda_client.settings.usda_api_key", None),
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

    async def test_db_error_in_seed_path_is_swallowed(self):
        with (
            patch("src.services.usda_client.settings.usda_api_key", None),
            patch(
                "src.tools.nutrition.get_first_nutrition",
                AsyncMock(return_value=None),
            ),
            patch(
                "src.tools.nutrition.get_ingredient_by_name",
                side_effect=SQLAlchemyError("db down"),
            ),
        ):
            result = await lookup_nutrition("apple")
            assert result["source"] == "unavailable"

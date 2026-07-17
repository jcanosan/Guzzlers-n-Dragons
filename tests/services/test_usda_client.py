"""Unit tests for USDA FoodData Central client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.usda_client import (
    _extract_nutrients,
    get_nutrition,
    search_food,
)


@pytest.fixture
def mock_usda(monkeypatch):
    """Mock httpx.AsyncClient for tests that call USDA API.

    Opt-in per test (not autouse in conftest) because only tests
    exercising search_food / get_nutrition need HTTP mocking.
    Pure-function tests (TestExtractNutrients) should run without it.
    """
    monkeypatch.setattr(
        "src.services.usda_client.settings.usda_api_key", "test_key"
    )
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    with patch(
        "src.services.usda_client.httpx.AsyncClient",
        return_value=mock_client,
    ):
        yield mock_client


class TestExtractNutrients:
    def test_empty(self):
        result = _extract_nutrients([])
        assert result == {}

    def test_known_nutrients(self):
        nutrients = [
            {"nutrientId": 1008, "amount": 365},
            {"nutrientId": 1003, "amount": 9.4},
            {"nutrientId": 1005, "amount": 74},
            {"nutrientId": 1004, "amount": 1.2},
        ]
        result = _extract_nutrients(nutrients)
        assert result["calories"] == 365
        assert result["protein_g"] == 9.4
        assert result["carbs_g"] == 74
        assert result["fat_g"] == 1.2

    def test_unknown_nutrients_ignored(self):
        nutrients = [
            {"nutrientId": 9999, "amount": 50},
            {"nutrientId": 1008, "amount": 100},
        ]
        result = _extract_nutrients(nutrients)
        assert result == {"calories": 100}


class TestSearchFoodNoApiKey:
    async def test_returns_empty(self, monkeypatch):
        monkeypatch.setattr(
            "src.services.usda_client.settings.usda_api_key", None
        )
        result = await search_food("apple")
        assert result == []


class TestGetNutritionNoApiKey:
    async def test_returns_none(self, monkeypatch):
        monkeypatch.setattr(
            "src.services.usda_client.settings.usda_api_key", None
        )
        result = await get_nutrition(12345)
        assert result is None


class TestSearchFood:
    async def test_mocked_response(self, mock_usda):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "foods": [{"fdcId": 12345, "description": "Apple, raw"}]
        }
        mock_usda.post.return_value = mock_response

        result = await search_food("apple")
        assert len(result) == 1
        assert result[0]["fdcId"] == 12345


class TestGetNutrition:
    async def test_mocked_response(self, mock_usda):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "foodNutrients": [
                {"nutrientId": 1008, "amount": 52},
                {"nutrientId": 1003, "amount": 0.3},
            ]
        }
        mock_usda.get.return_value = mock_response

        result = await get_nutrition(12345)
        assert result is not None
        assert result["calories"] == 52

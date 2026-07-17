"""Unit tests for Fineli API client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.fineli_client import get_nutrition, search_food


@pytest.fixture
def mock_fineli():
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    with patch(
        "src.services.fineli_client.httpx.AsyncClient",
        return_value=mock_client,
    ):
        yield mock_client


class TestSearchFood:
    async def test_mocked_search(self, mock_fineli):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": 33013, "name": {"en": "Apple"}}
        ]
        mock_fineli.get.return_value = mock_response

        result = await search_food("apple")
        assert len(result) == 1
        assert result[0]["id"] == 33013


class TestGetNutrition:
    async def test_mocked_nutrition(self, mock_fineli):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": 33013,
            "energyKcal": 52,
            "protein": 0.3,
            "carbohydrate": 14,
            "fat": 0.2,
            "fiber": 2.4,
        }
        mock_fineli.get.return_value = mock_response

        result = await get_nutrition(33013)
        assert result is not None
        assert result["calories"] == 52
        assert result["protein_g"] == 0.3

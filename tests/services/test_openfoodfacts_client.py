"""Unit tests for Open Food Facts API client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.openfoodfacts_client import (
    _extract_nutrients,
    get_first_nutrition,
    search_food,
)


@pytest.fixture
def mock_off():
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    with patch(
        "src.services.openfoodfacts_client.httpx.AsyncClient",
        return_value=mock_client,
    ):
        yield mock_client


class TestSearchFood:
    async def test_mocked_search(self, mock_off):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "products": [{"product_name": "Apple", "nutriments": {}}]
        }
        mock_off.get.return_value = mock_response

        result = await search_food("apple")
        assert len(result) == 1
        assert result[0]["product_name"] == "Apple"


class TestExtractNutrients:
    def test_first_product_with_data(self):
        products = [
            {
                "product_name": "Apple Juice",
                "nutriments": {
                    "energy-kcal_100g": 46,
                    "proteins_100g": 0.1,
                },
            }
        ]
        result = _extract_nutrients(products)
        assert result is not None
        assert result["calories"] == 46
        assert result["source"] == "open_food_facts"

    def test_no_products(self):
        result = _extract_nutrients([])
        assert result is None

    def test_skip_missing_nutriments(self):
        products = [
            {"product_name": "Empty", "nutriments": {}},
            {
                "product_name": "Cereal",
                "nutriments": {"energy-kcal_100g": 200},
            },
        ]
        result = _extract_nutrients(products)
        assert result is not None
        assert result["calories"] == 200


class TestGetFirstNutrition:
    async def test_delegates(self, mock_off):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "products": [
                {
                    "product_name": "Milk",
                    "nutriments": {"energy-kcal_100g": 65},
                }
            ]
        }
        mock_off.get.return_value = mock_response

        result = await get_first_nutrition("milk")
        assert result is not None
        assert result["calories"] == 65

"""Unit tests for TheMealDB client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.themealdb_client import (
    extract_ingredient_pairs,
    extract_techniques,
    get_meal_details,
    search_meals,
)


@pytest.fixture
def mock_themealdb():
    """Mock httpx.AsyncClient for tests that call TheMealDB API.

    Opt-in per test (not autouse in conftest) because only tests
    exercising search_meals / get_meal_details need HTTP mocking.
    Pure-function tests (extract_techniques, extract_ingredient_pairs)
    should run without it.
    """
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    with patch(
        "src.services.themealdb_client.httpx.AsyncClient",
        return_value=mock_client,
    ):
        yield mock_client


class TestExtractTechniques:
    def test_basic(self):
        result = extract_techniques(
            "Boil the pasta. Then sauté the garlic in olive oil."
        )
        assert "boil" in result
        assert "sauté" in result

    def test_empty(self):
        result = extract_techniques("")
        assert result == []

    def test_none(self):
        result = extract_techniques(None)
        assert result == []

    def test_duplicates_removed(self):
        result = extract_techniques("boil water, boil again, then bake")
        assert result == ["bake", "boil"]


class TestExtractIngredientPairs:
    def test_multiple_ingredients(self):
        meal = {
            "strIngredient1": "Chicken",
            "strMeasure1": "500g",
            "strIngredient2": "Garlic",
            "strMeasure2": "2 cloves",
            "strIngredient3": "",
            "strMeasure3": "",
        }
        result = extract_ingredient_pairs(meal)
        assert len(result) == 2
        assert result[0] == {"ingredient": "Chicken", "amount": "500g"}

    def test_empty_ingredients(self):
        meal = {"strIngredient1": "", "strMeasure1": ""}
        result = extract_ingredient_pairs(meal)
        assert result == []


class TestSearchMeals:
    async def test_results_found(self, mock_themealdb):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "meals": [{"idMeal": "52772", "strMeal": "Chicken"}]
        }
        mock_themealdb.get.return_value = mock_response

        result = await search_meals("chicken")
        assert len(result) == 1
        assert result[0]["strMeal"] == "Chicken"

    async def test_no_results(self, mock_themealdb):
        mock_response = MagicMock()
        mock_response.json.return_value = {"meals": None}
        mock_themealdb.get.return_value = mock_response

        result = await search_meals("xyznonexistent")
        assert result == []


class TestGetMealDetails:
    async def test_results_found(self, mock_themealdb):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "meals": [
                {
                    "idMeal": "52772",
                    "strMeal": "Chicken",
                    "strInstructions": "Boil and sauté",
                }
            ]
        }
        mock_themealdb.get.return_value = mock_response

        result = await get_meal_details("52772")
        assert result is not None
        assert result["strMeal"] == "Chicken"

    async def test_not_found(self, mock_themealdb):
        mock_response = MagicMock()
        mock_response.json.return_value = {"meals": None}
        mock_themealdb.get.return_value = mock_response

        result = await get_meal_details("99999")
        assert result is None

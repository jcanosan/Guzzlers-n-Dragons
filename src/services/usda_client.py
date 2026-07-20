"""USDA FoodData Central API client for nutrition lookups of real food."""

import httpx
import structlog

from src.config.settings import settings

logger = structlog.get_logger()

USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"


async def search_food(query: str, page_size: int = 5) -> list[dict]:
    """Search USDA for a food item by name.

    Returns a list of matching foods with FDC IDs and basic info.
    Returns empty list if API key is missing or request fails.
    """
    if not settings.usda_api_key:
        logger.warning("usda_skipped", reason="missing_api_key")
        return []

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.post(
                f"{USDA_BASE_URL}/foods/search",
                headers={"X-Api-Key": settings.usda_api_key},
                json={
                    "query": query,
                    "pageSize": page_size,
                    "dataType": ["Foundation", "SR Legacy"],
                },
            )
            response.raise_for_status()
            data = response.json()
            foods = data.get("foods", [])
            logger.info("usda_search", query=query, result_count=len(foods))
            return foods
        except httpx.HTTPError as exc:
            logger.error(
                "usda_search_failed",
                query=query,
                error_type=type(exc).__name__,
            )
            return []


async def get_nutrition(fdc_id: int) -> dict | None:
    """Get detailed nutrition data for a food by FDC ID.

    Returns a dict with nutrients per 100g, or None if unavailable.
    """
    if not settings.usda_api_key:
        logger.warning("usda_skipped", reason="missing_api_key")
        return None

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(
                f"{USDA_BASE_URL}/food/{fdc_id}",
                headers={"X-Api-Key": settings.usda_api_key},
            )
            response.raise_for_status()
            data = response.json()
            nutrients = _extract_nutrients(
                food_nutrients=data.get("foodNutrients", [])
            )
            logger.info("usda_nutrition", fdc_id=fdc_id)
            return nutrients
        except httpx.HTTPError as exc:
            logger.error(
                "usda_nutrition_failed",
                fdc_id=fdc_id,
                error_type=type(exc).__name__,
            )
            return None


def _extract_nutrients(food_nutrients: list[dict]) -> dict:
    """Extract key nutrition values per 100g from raw USDA data."""
    nutrient_map = {}
    target_ids = {
        1008: "calories",  # Energy (kcal)
        1003: "protein_g",  # Protein
        1005: "carbs_g",  # Carbohydrate
        1004: "fat_g",  # Total fat
        1079: "fiber_g",  # Fiber
        1253: "cholesterol_mg",  # Cholesterol
        1258: "saturated_fat_g",  # Saturated fat
        1257: "trans_fat_g",  # Trans fat
    }

    for nutrient in food_nutrients:
        nutrient_id = nutrient.get("nutrientId")
        if nutrient_id in target_ids:
            amount = nutrient.get("amount", 0)
            nutrient_map[target_ids[nutrient_id]] = amount

    return nutrient_map

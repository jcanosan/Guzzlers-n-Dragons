"""Fineli (Finnish Institute for Health and Welfare) API client.

Government-authority food composition data, lab-analysed, no API key needed.
REST/JSON. Covers ~3,800 foods. English names available.
"""

import httpx
import structlog

logger = structlog.get_logger()

FINELI_BASE_URL = "https://fineli.fi/fineli/api/v1"


async def search_food(query: str, page_size: int = 5) -> list[dict]:
    """Search Fineli for a food item by name.

    Returns raw food list with id and name.en fields.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(
                f"{FINELI_BASE_URL}/foods",
                params={"q": query},
            )
            response.raise_for_status()
            foods = response.json()
            logger.info("fineli_search", query=query, result_count=len(foods))
            return foods[:page_size]
        except (httpx.HTTPError, ValueError) as exc:
            logger.error(
                "fineli_search_failed",
                query=query,
                error_type=type(exc).__name__,
            )
            return []


async def get_nutrition(food_id: int) -> dict | None:
    """Get nutrition data for a food by Fineli ID.

    Returns dict with calories, fat, protein, carbohydrate, fiber per 100g.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(
                f"{FINELI_BASE_URL}/foods/{food_id}",
            )
            response.raise_for_status()
            data = response.json()
            nutrients = {
                "calories": data.get("energyKcal"),
                "protein_g": data.get("protein"),
                "carbs_g": data.get("carbohydrate"),
                "fat_g": data.get("fat"),
                "fiber_g": data.get("fiber"),
                "sugar_g": data.get("sugar"),
                "saturated_fat_g": data.get("saturatedFat"),
            }
            logger.info("fineli_nutrition", food_id=food_id)
            return {k: v for k, v in nutrients.items() if v is not None}
        except (httpx.HTTPError, ValueError) as exc:
            logger.error(
                "fineli_nutrition_failed",
                food_id=food_id,
                error_type=type(exc).__name__,
            )
            return None

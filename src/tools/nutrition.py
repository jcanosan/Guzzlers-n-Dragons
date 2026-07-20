"""Nutrition lookup chain: USDA → Fineli → Open Food Facts → DB."""

import structlog

from src.services.database import get_ingredient_by_name
from src.services.fineli_client import get_nutrition as fineli_get_nutrition
from src.services.fineli_client import search_food as fineli_search_food
from src.services.openfoodfacts_client import get_first_nutrition
from src.services.usda_client import get_nutrition, search_food

logger = structlog.get_logger()


async def lookup_nutrition(ingredient_name: str) -> dict:
    """Look up nutrition data, chaining USDA → Fineli → Open Food Facts → DB."""
    usda = await _try_usda_nutrition(ingredient_name)
    if usda:
        return usda

    fineli = await _try_fineli_nutrition(ingredient_name)
    if fineli:
        return fineli

    off = await _try_off_nutrition(ingredient_name)
    if off:
        return off

    seed = await _try_seed_nutrition(ingredient_name)
    if seed:
        return seed

    logger.warning("nutrition_unavailable", ingredient=ingredient_name)
    return _unavailable_result()


async def _try_usda_nutrition(ingredient_name: str) -> dict | None:
    foods = await search_food(ingredient_name)
    if not foods:
        logger.info("usda_no_match", ingredient=ingredient_name)
        return None

    fdc_id = foods[0].get("fdcId")
    if not fdc_id:
        logger.info("usda_no_fdc_id", ingredient=ingredient_name)
        return None

    nutrients = await get_nutrition(fdc_id)
    if not nutrients:
        logger.info("usda_no_nutrients", fdc_id=fdc_id)
        return None

    logger.info("usda_nutrition_found", ingredient=ingredient_name)
    return {
        "calories_per_serving": nutrients.get("calories"),
        "protein_g": nutrients.get("protein_g"),
        "carbs_g": nutrients.get("carbs_g"),
        "fat_g": nutrients.get("fat_g"),
        "fiber_g": nutrients.get("fiber_g"),
        "source": "usda",
    }


async def _try_fineli_nutrition(ingredient_name: str) -> dict | None:
    foods = await fineli_search_food(ingredient_name)
    if not foods:
        return None

    food_id = foods[0].get("id")
    if not food_id:
        return None

    nutrients = await fineli_get_nutrition(food_id)
    if not nutrients:
        return None

    logger.info("fineli_nutrition_found", ingredient=ingredient_name)
    return {
        "calories_per_serving": nutrients.get("calories"),
        "protein_g": nutrients.get("protein_g"),
        "carbs_g": nutrients.get("carbs_g"),
        "fat_g": nutrients.get("fat_g"),
        "fiber_g": nutrients.get("fiber_g"),
        "source": "fineli",
    }


async def _try_off_nutrition(ingredient_name: str) -> dict | None:
    nutrients = await get_first_nutrition(ingredient_name)
    if not nutrients:
        return None

    logger.info("off_nutrition_found", ingredient=ingredient_name)
    return {
        "calories_per_serving": nutrients.get("calories"),
        "protein_g": nutrients.get("protein_g"),
        "carbs_g": nutrients.get("carbs_g"),
        "fat_g": nutrients.get("fat_g"),
        "fiber_g": nutrients.get("fiber_g"),
        "source": "open_food_facts",
    }


async def _try_seed_nutrition(ingredient_name: str) -> dict | None:
    fictional = get_ingredient_by_name(ingredient_name)
    if not fictional or not fictional.real_world_approximations:
        logger.info("seed_no_match", ingredient=ingredient_name)
        return None

    logger.info("seed_match", ingredient=ingredient_name)
    return {
        "calories_per_serving": None,
        "protein_g": None,
        "carbs_g": None,
        "fat_g": None,
        "fiber_g": None,
        "source": "approximation",
        "approximations": fictional.real_world_approximations,
    }


def _unavailable_result() -> dict:
    return {
        "calories_per_serving": None,
        "protein_g": None,
        "carbs_g": None,
        "fat_g": None,
        "fiber_g": None,
        "source": "unavailable",
    }

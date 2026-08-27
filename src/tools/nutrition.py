"""Nutrition lookup chain: USDA → Open Food Facts → DB."""

from typing import NotRequired, TypedDict

import structlog
from sqlalchemy.exc import SQLAlchemyError

from src.agents.llm import call_llm
from src.schemas.domain import FictionalIngredient
from src.services.database import get_ingredient_by_name
from src.services.openfoodfacts_client import get_first_nutrition
from src.services.usda_client import get_nutrition, search_food

logger = structlog.get_logger()

APPROXIMATION_SYSTEM_PROMPT = (
    "You map a fictional food ingredient to the single closest real-world"
    " ingredient a nutrition database would recognize.\n"
    "Reply with ONLY the real ingredient name. No quotes, no explanations,"
    " no recipe, no list. Strip any fictional modifiers (mutant, golden,"
    " magical, etc.).\n"
    "Examples:\n"
    "  mutant cow milk -> cow milk\n"
    "  manticore leg -> venison leg\n"
    "  blue dragon pepper -> bell pepper"
)


class NutritionResult(TypedDict):
    """Contract for all nutrition lookup return values."""

    calories_per_serving: float | None
    protein_g: float | None
    carbs_g: float | None
    fat_g: float | None
    fiber_g: float | None
    source: str
    approximations: NotRequired[list[dict]]


async def resolve_approximation(
    ingredient_name: str, profile: FictionalIngredient | None
) -> str:
    """Resolve the real-world ingredient to query nutrition for.

    Prefers a seeded approximation, else asks the LLM to map the
    fictional name to a real ingredient. Falls back to the raw name if
    the LLM call or parse fails.
    """
    if profile and profile.real_world_approximations:
        return profile.real_world_approximations[0]["ingredient"]

    try:
        response = await call_llm(
            APPROXIMATION_SYSTEM_PROMPT,
            f"Fictional ingredient: {ingredient_name}",
        )
        approx = str(response.content).strip().strip('"').strip(".")
        if approx and "->" not in approx:
            logger.info(
                "llm_approximation", ingredient=ingredient_name, approx=approx
            )
            return approx
    except Exception:
        logger.warning(
            "llm_approximation_failed",
            ingredient=ingredient_name,
            exc_info=True,
        )

    return ingredient_name


async def lookup_nutrition(ingredient_name: str) -> NutritionResult:
    """Look up nutrition data, chaining USDA → Open Food Facts → DB."""
    usda = await _try_usda_nutrition(ingredient_name)
    if usda:
        return usda

    off = await _try_off_nutrition(ingredient_name)
    if off:
        return off

    seed = await _try_seed_nutrition(ingredient_name)
    if seed:
        return seed

    logger.warning("nutrition_unavailable", ingredient=ingredient_name)
    return _unavailable_result()


async def _try_usda_nutrition(ingredient_name: str) -> NutritionResult | None:
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


async def _try_off_nutrition(ingredient_name: str) -> NutritionResult | None:
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


async def _try_seed_nutrition(ingredient_name: str) -> NutritionResult | None:
    try:
        fictional = get_ingredient_by_name(ingredient_name)
    except SQLAlchemyError as exc:
        logger.error(
            "seed_nutrition_failed", ingredient=ingredient_name, error=str(exc)
        )
        return None
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


def _unavailable_result() -> NutritionResult:
    return {
        "calories_per_serving": None,
        "protein_g": None,
        "carbs_g": None,
        "fat_g": None,
        "fiber_g": None,
        "source": "unavailable",
    }

"""TheMealDB API client for pattern extraction from real recipes."""

import httpx
import structlog

logger = structlog.get_logger()

MEALDB_BASE_URL = "https://www.themealdb.com/api/json/v1/1"

# Known cooking techniques to extract from instructions
_TECHNIQUES_KEYWORDS = {
    "bake",
    "boil",
    "braise",
    "broil",
    "chop",
    "dice",
    "emulsify",
    "ferment",
    "fry",
    "grill",
    "marinate",
    "mince",
    "poach",
    "roast",
    "sauté",
    "simmer",
    "steam",
    "stir-fry",
    "whisk",
}


async def search_meals(ingredient: str) -> list[dict]:
    """Search TheMealDB for meals containing a given ingredient."""
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(
                f"{MEALDB_BASE_URL}/filter.php",
                params={"i": ingredient},
            )
            response.raise_for_status()
            data = response.json()
            meals = data.get("meals") or []
            logger.info(
                "themealdb_search", ingredient=ingredient, count=len(meals)
            )
            return meals
        except (httpx.HTTPError, ValueError) as exc:
            logger.error(
                "themealdb_search_failed",
                ingredient=ingredient,
                error_type=type(exc).__name__,
            )
            return []


async def get_meal_details(meal_id: str) -> dict | None:
    """Get full meal details including instructions and ingredient list."""
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(
                f"{MEALDB_BASE_URL}/lookup.php",
                params={"i": meal_id},
            )
            response.raise_for_status()
            data = response.json()
            meals = data.get("meals")
            if meals:
                return meals[0]
            return None
        except (httpx.HTTPError, ValueError) as exc:
            logger.error(
                "themealdb_details_failed",
                meal_id=meal_id,
                error_type=type(exc).__name__,
            )
            return None


def extract_techniques(instructions: str | None) -> list[str]:
    """Extract cooking techniques from recipe instructions."""
    if not instructions:
        return []

    text_lower = instructions.lower()
    found = {
        technique
        for technique in _TECHNIQUES_KEYWORDS
        if technique in text_lower
    }
    return sorted(found)


def extract_ingredient_pairs(meal: dict) -> list[dict[str, str]]:
    """Extract ingredient pairings from a meal.

    TheMealDB stores up to 20 ingredients as strIngredient1..20
    with corresponding strMeasure1..20 for amounts.
    """
    pairs = []
    for i in range(1, 21):
        ingredient = meal.get(f"strIngredient{i}", "").strip()
        measure = meal.get(f"strMeasure{i}", "").strip()
        if ingredient:
            pairs.append({"ingredient": ingredient, "amount": measure})
    return pairs


async def find_recipe_patterns(ingredient: str) -> list[dict]:
    """Find real-world recipe patterns using a given ingredient.

    Returns meals with techniques, ingredient lists, and metadata.
    """
    meals = await search_meals(ingredient)
    if not meals:
        return []

    patterns = []
    for meal in meals[:5]:
        meal_id = meal.get("idMeal")
        if not meal_id:
            continue
        details = await get_meal_details(meal_id)
        if details is None:
            continue

        instructions = details.get("strInstructions", "")
        patterns.append(
            {
                "name": details.get("strMeal"),
                "category": details.get("strCategory"),
                "area": details.get("strArea"),
                "techniques": extract_techniques(instructions),
                "ingredients": extract_ingredient_pairs(details),
                "instructions": instructions,
            }
        )

    logger.info("recipe_patterns_extracted", count=len(patterns))
    return patterns

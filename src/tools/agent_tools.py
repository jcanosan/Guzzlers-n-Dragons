"""Agent tools for nutrition and recipe-pattern lookups.

Each tool is decorated with LangChain's @tool, providing:
- Structured input schema (auto-inferred from type hints)
- Natural-language description for agent tool selection
- Typed return value

Tools can be loaded into a LangGraph agent via ToolNode.
The agent discovers tools at runtime and selects which to call
based on the task description.
"""

from langchain_core.tools import tool

from src.services.themealdb_client import find_recipe_patterns
from src.tools.nutrition import lookup_nutrition
from src.tools.validation import validate_ingredient


@tool
async def lookup_ingredient_nutrition(ingredient_name: str) -> dict:
    """Look up nutrition data for an ingredient with multi-source fallback.

    Tries USDA first, then Fineli (EU government data), then Open Food Facts,
    then the seeded ingredient database. Returns macros and data source.

    Args:
        ingredient_name: Name of the ingredient to look up
    """
    ingredient_name = validate_ingredient(ingredient_name)
    return await lookup_nutrition(ingredient_name)


@tool
async def find_recipes_by_ingredient(ingredient: str) -> list[dict]:
    """Find real-world recipes containing a given ingredient.

    Uses TheMealDB to find meals, then extracts cooking techniques
    and ingredient pairings. Returns structured recipes with name,
    category, techniques, and ingredient lists.

    Args:
        ingredient: Ingredient name to search for (e.g., 'chicken', 'flour')
    """
    ingredient = validate_ingredient(ingredient)
    return await find_recipe_patterns(ingredient)


@tool
async def get_common_cooking_techniques(ingredient: str) -> list[str]:
    """Get common cooking techniques used with a given ingredient.

    Searches TheMealDB for recipes containing the ingredient, then
    extracts and aggregates techniques across them.

    Args:
        ingredient: Ingredient name to analyze
    """
    ingredient = validate_ingredient(ingredient)
    patterns = await find_recipe_patterns(ingredient)
    techniques: set[str] = set()
    for pattern in patterns:
        techniques.update(pattern.get("techniques", []))
    return sorted(techniques)


# Tool registry: all tools the agent can discover and call
ALL_AGENT_TOOLS = [
    lookup_ingredient_nutrition,
    find_recipes_by_ingredient,
    get_common_cooking_techniques,
]

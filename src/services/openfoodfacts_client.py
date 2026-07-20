"""Open Food Facts API client (crowd-sourced, global, no API key needed).

Fallback nutrition source when USDA and Fineli are unavailable.
Product-based (branded foods), not ingredient-based like USDA/Fineli.
Rate-limited for anonymous requests; use as last resort only.
"""

import httpx
import structlog

logger = structlog.get_logger()

OFF_BASE_URL = "https://world.openfoodfacts.org"


async def search_food(query: str, page_size: int = 3) -> list[dict]:
    """Search Open Food Facts for a food product by name.

    Returns products with nutriments per 100g.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(
                f"{OFF_BASE_URL}/cgi/search.pl",
                params={
                    "search_terms": query,
                    "json": "true",
                    "page_size": page_size,
                },
            )
            response.raise_for_status()
            data = response.json()
            products = data.get("products", [])
            logger.info("off_search", query=query, result_count=len(products))
            return products
        except (httpx.HTTPError, ValueError) as exc:
            logger.error(
                "off_search_failed",
                query=query,
                error_type=type(exc).__name__,
            )
            return []


def _extract_nutrients(products: list[dict]) -> dict | None:
    """Extract nutrition per 100g from the first product that has data."""
    for product in products:
        nutriments = product.get("nutriments") or {}
        if not nutriments:
            continue
        kcal = nutriments.get("energy-kcal_100g")
        if kcal is None:
            continue

        return {
            "calories": kcal,
            "protein_g": nutriments.get("proteins_100g"),
            "carbs_g": nutriments.get("carbohydrates_100g"),
            "fat_g": nutriments.get("fat_100g"),
            "fiber_g": nutriments.get("fiber_100g"),
            "sugar_g": nutriments.get("sugars_100g"),
            "source": "open_food_facts",
            "product_name": product.get("product_name"),
        }
    return None


async def get_first_nutrition(query: str) -> dict | None:
    """Quick lookup: search Open Food Facts, return nutrition of top result."""
    products = await search_food(query)
    return _extract_nutrients(products)

from fastapi import APIRouter, HTTPException, status

from src.schemas.domain import FictionalIngredient
from src.schemas.request import AlchemyRequest
from src.schemas.response import AlchemyResult
from src.services.database import get_ingredient_by_name, list_ingredients

router = APIRouter()


@router.post(
    "/transform", response_model=AlchemyResult, status_code=status.HTTP_200_OK
)
async def transform_ingredient(request: AlchemyRequest):
    """Transform a fictional ingredient into a plausible recipe."""
    # TODO: Implement agent pipeline
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Agent pipeline not yet implemented",
    )


@router.get("/ingredients", response_model=list[FictionalIngredient])
async def get_ingredients(thematic_group: str | None = None):
    """List available fictional ingredients, optionally filtered by theme."""
    ingredients = list_ingredients(thematic_group)
    return ingredients


@router.get(
    "/ingredients/{ingredient_name}", response_model=FictionalIngredient
)
async def get_ingredient(ingredient_name: str):
    """Get details for a specific fictional ingredient."""
    ingredient = get_ingredient_by_name(ingredient_name)
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient '{ingredient_name}' not found",
        )
    return ingredient

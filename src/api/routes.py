from fastapi import APIRouter, HTTPException, status

from src.agents.graph import agent_graph
from src.schemas.agents import AgentState
from src.schemas.domain import FictionalIngredient
from src.schemas.request import AlchemyRequest
from src.schemas.response import AlchemyResult, PlausibilityReport, Recipe
from src.services.database import get_ingredient_by_name, list_ingredients

router = APIRouter()


@router.post(
    "/transform",
    response_model=AlchemyResult,
    status_code=status.HTTP_200_OK,
)
async def transform_ingredient(request: AlchemyRequest):
    """Transform a fictional ingredient into a plausible recipe.

    Runs the Planner → Creator → Critic LangGraph pipeline
    with up to 3 feedback-loop iterations.
    """
    initial_state = AgentState(request=request)
    final_state = await agent_graph.ainvoke(initial_state)

    report = PlausibilityReport(**(final_state["report"] or {}))
    draft = final_state.get("draft_recipe")

    recipe = Recipe(
        name=draft.name if draft else "",
        description=draft.description if draft else "",
        ingredients=draft.ingredients if draft else [],
        instructions=draft.instructions if draft else [],
        prep_time_minutes=draft.prep_time_minutes if draft else 0,
        cook_time_minutes=draft.cook_time_minutes if draft else 0,
        servings=draft.servings if draft else 0,
        difficulty=draft.difficulty if draft else "medium",
    )

    return AlchemyResult(
        recipe=recipe,
        plausibility_report=report,
        metadata={
            "iterations": final_state.get("iteration", 0),
            "ingredient": request.fictional_ingredient,
        },
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

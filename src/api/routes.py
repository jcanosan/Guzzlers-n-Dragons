import asyncio

from fastapi import APIRouter, HTTPException, status

from src.agents.graph import agent_graph
from src.schemas.agents import AgentState
from src.schemas.domain import FictionalIngredient
from src.schemas.request import AlchemyRequest
from src.schemas.response import AlchemyResult, PlausibilityReport, Recipe
from src.services.database import get_ingredient_by_name, list_ingredients

router = APIRouter()

AGENT_TIMEOUT_SECONDS = 300


def _get(draft, key: str, default=None):
    """Extract a value from a dict or object, falling back to default."""
    if isinstance(draft, dict):
        return draft.get(key, default)
    return getattr(draft, key, default) if draft else default


def _build_result(final_state: dict, request: AlchemyRequest) -> AlchemyResult:
    """Build an AlchemyResult from the final graph state.

    Degrades gracefully: empty report/draft if the state is partial.
    """
    report = PlausibilityReport(**(final_state.get("report", {}) or {}))
    draft = final_state.get("draft_recipe")

    recipe = Recipe(
        name=_get(draft, "name", ""),
        description=_get(draft, "description", ""),
        ingredients=_get(draft, "ingredients", []),
        instructions=_get(draft, "instructions", []),
        prep_time_minutes=_get(draft, "prep_time_minutes", 0),
        cook_time_minutes=_get(draft, "cook_time_minutes", 0),
        servings=_get(draft, "servings", 0),
        difficulty=_get(draft, "difficulty", "medium"),
    )

    return AlchemyResult(
        recipe=recipe,
        plausibility_report=report,
        metadata={
            "iterations": final_state.get("iteration", 0),
            "ingredient": request.fictional_ingredient,
        },
    )


@router.post(
    "/transform",
    response_model=AlchemyResult,
    status_code=status.HTTP_200_OK,
)
async def transform_ingredient(request: AlchemyRequest):
    """Transform a fictional ingredient into a plausible recipe.

    Runs the Planner -> Creator -> Critic LangGraph pipeline with up to
    3 feedback-loop iterations. Degrades gracefully on partial output.
    """
    initial_state = AgentState(request=request)

    try:
        final_state = await asyncio.wait_for(
            agent_graph.ainvoke(initial_state),
            timeout=AGENT_TIMEOUT_SECONDS,
        )
    except TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Agent pipeline timed out. The LLM or external API "
            "may be unresponsive. Retry with a simpler ingredient.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Agent pipeline failed: {type(exc).__name__}",
        ) from exc

    return _build_result(final_state, request)


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

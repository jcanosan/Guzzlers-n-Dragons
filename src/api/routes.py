import asyncio

import structlog
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.agents.graph import agent_graph
from src.api.streaming import AgentEventStream
from src.config.settings import settings
from src.schemas.agents import AgentState
from src.schemas.domain import FictionalIngredient
from src.schemas.request import AlchemyRequest
from src.schemas.response import AlchemyResult, PlausibilityReport, Recipe
from src.services.database import get_ingredient_by_name, list_ingredients

router = APIRouter()

logger = structlog.get_logger()

AGENT_TIMEOUT_SECONDS = settings.agent_timeout_seconds
SSE_PING_INTERVAL_SECONDS = 15.0

limiter = Limiter(key_func=get_remote_address)


def _limit():
    """Apply the configured rate limit, or no-op when disabled."""
    if settings.rate_limit_enabled:
        return limiter.limit(settings.rate_limit)
    return lambda fn: fn


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
@_limit()
async def transform_ingredient(
    request: Request, body: AlchemyRequest
) -> AlchemyResult:
    """Transform a fictional ingredient into a plausible recipe.

    Runs the Planner -> Creator -> Critic LangGraph pipeline with up to
    3 feedback-loop iterations. Degrades gracefully on partial output.
    """
    initial_state = AgentState(request=body)

    try:
        final_state = await asyncio.wait_for(
            agent_graph.ainvoke(initial_state),
            timeout=AGENT_TIMEOUT_SECONDS,
        )
        return _build_result(final_state, body)
    except TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Agent pipeline timed out. The LLM or external API "
            "may be unresponsive. Retry with a simpler ingredient.",
        )
    except Exception as exc:
        logger.exception("agent_pipeline_failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Agent pipeline failed",
        ) from exc


@router.post("/transform/stream")
@_limit()
async def transform_stream(request: Request, body: AlchemyRequest):
    """Stream the Planner -> Creator -> Critic pipeline as SSE.

    Emits a `node` event per completed stage, an `error` event on
    failure, and a `done` event on success.
    """
    relay = AgentEventStream(
        body,
        timeout_seconds=AGENT_TIMEOUT_SECONDS,
        ping_interval_seconds=SSE_PING_INTERVAL_SECONDS,
    )
    return StreamingResponse(relay.events(), media_type="text/event-stream")


@router.get("/ingredients", response_model=list[FictionalIngredient])
async def get_ingredients(thematic_group: str | None = None):
    """List available fictional ingredients, optionally filtered by theme."""
    ingredients = await asyncio.to_thread(list_ingredients, thematic_group)
    return ingredients


@router.get(
    "/ingredients/{ingredient_name}", response_model=FictionalIngredient
)
async def get_ingredient(ingredient_name: str):
    """Get details for a specific fictional ingredient."""
    ingredient = await asyncio.to_thread(
        get_ingredient_by_name, ingredient_name
    )
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient '{ingredient_name}' not found",
        )
    return ingredient

import asyncio
import json

import structlog
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.agents.graph import agent_graph
from src.config.settings import settings
from src.schemas.agents import AgentState
from src.schemas.domain import FictionalIngredient
from src.schemas.request import AlchemyRequest
from src.schemas.response import AlchemyResult, PlausibilityReport, Recipe
from src.services.database import get_ingredient_by_name, list_ingredients

router = APIRouter()

logger = structlog.get_logger()

AGENT_TIMEOUT_SECONDS = settings.agent_timeout_seconds

limiter = Limiter(key_func=get_remote_address)


def _limit():
    """Apply the configured rate limit, or no-op when disabled."""
    if settings.rate_limit_enabled:
        return limiter.limit(settings.rate_limit)
    return lambda fn: fn


def _sse_event(name: str, payload: dict) -> str:
    """Format a Server-Sent Events message."""
    return f"event: {name}\ndata: {json.dumps(payload, default=str)}\n\n"


def _dump(value: object) -> dict:
    """Serialize a pydantic model to a dict, or return {}."""
    dump = getattr(value, "model_dump", None)
    return dump() if callable(dump) else {}


def _node_update(node: str, update: dict) -> dict | None:
    """Curate a node's state update into a serializable payload."""
    if node == "planner":
        return {
            "iteration": update.get("iteration", 0),
            "planner_result": _dump(update.get("planner_result")),
        }
    if node == "creator":
        return {"draft_recipe": _dump(update.get("draft_recipe"))}
    if node == "critic":
        return {"report": update.get("report") or {}}
    return None


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

    Emits a `node` event per completed stage with its state update, an
    `error` event on failure, and a `done` event on success. The graph is
    sequential, so the frontend infers running-stage from completion order.
    """

    async def event_source():
        initial_state = AgentState(request=body)
        try:
            async with asyncio.timeout(AGENT_TIMEOUT_SECONDS):
                async for chunk in agent_graph.astream(
                    initial_state, stream_mode="updates"
                ):
                    if not isinstance(chunk, dict):
                        continue
                    for node, update in chunk.items():
                        payload = _node_update(node, update)
                        if payload:
                            yield _sse_event(
                                "node",
                                {
                                    "node": node,
                                    "stage": "end",
                                    "data": payload,
                                },
                            )
            yield _sse_event("done", {})
        except TimeoutError:
            logger.warning("agent_stream_timeout")
            yield _sse_event("error", {"message": "Agent pipeline timed out"})
        except Exception as exc:
            logger.exception("agent_stream_failed")
            yield _sse_event(
                "error", {"message": f"{type(exc).__name__}: {exc}"}
            )

    return StreamingResponse(event_source(), media_type="text/event-stream")


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

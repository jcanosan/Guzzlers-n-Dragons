"""Promptfoo Python provider wrapping the compiled LangGraph alchemy pipeline.

Receives one eval case's vars, runs the real Planner -> Creator -> Critic
graph, and returns a JSON string containing the final recipe, the Critic
report, and the iteration count.

Usage:
    PYTHONPATH=. npx promptfoo eval -c evals/promptfooconfig.yaml
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

ROOT = str(Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.services.database import init_db  # noqa: E402
from src.services.vector_store import vector_store  # noqa: E402

_seeded = False
_loop: asyncio.AbstractEventLoop | None = None


def _split_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    return [p.strip() for p in str(value).split(",") if p.strip()]


def _init() -> None:
    global _seeded
    if not _seeded:
        init_db()
        vector_store.init()
        _seeded = True


async def run_pipeline(variables: dict[str, Any]) -> str:
    from src.agents.graph import agent_graph
    from src.schemas.agents import AgentState
    from src.schemas.request import AlchemyRequest, Constraints

    request = AlchemyRequest(
        fictional_ingredient=str(variables["ingredient"]),
        meal_type=str(variables.get("meal_type", "main course")),
        thematic_group=str(variables["theme"]),
        constraints=Constraints(
            servings=int(variables.get("servings", 4)),
            dietary=_split_list(variables.get("dietary")),
            difficulty=variables.get("difficulty") or None,
        ),
    )
    state: dict[str, Any] = {}
    async for chunk in agent_graph.astream(
        AgentState(request=request), stream_mode="updates"
    ):
        for update in chunk.values():
            state.update(update)
    recipe = state.get("draft_recipe")
    report = state.get("report") or {}
    result = {
        "recipe": recipe.model_dump() if recipe else None,
        "report": report,
        "iterations": state.get("iteration", 0),
    }
    return json.dumps(result, default=str)


def _run(coro: Any) -> Any:
    global _loop
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
    return _loop.run_until_complete(coro)


def call_api(
    prompt: str,
    options: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, str]:
    """Promptfoo provider entry point. The passthrough prompt is unused."""
    _init()
    try:
        output = _run(run_pipeline(dict(context["vars"])))
    except Exception as exc:  # promptfoo renders the error per case
        return {"error": f"{type(exc).__name__}: {exc}"}
    return {"output": output}

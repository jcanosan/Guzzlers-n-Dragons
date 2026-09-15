"""SSE relay for the agent graph.

Turns ``agent_graph.astream`` updates into server-sent events with
keepalive pings, so idle proxy connections survive long LLM calls.
"""

import asyncio
import contextlib
import json
from collections.abc import AsyncIterator

import structlog

from src.agents.graph import agent_graph
from src.schemas.agents import AgentState
from src.schemas.request import AlchemyRequest

logger = structlog.get_logger()


def _sse_event(name: str, payload: dict) -> str:
    """Format one Server-Sent Events message."""
    return f"event: {name}\ndata: {json.dumps(payload, default=str)}\n\n"


def _dump(value: object) -> dict:
    """Serialize a pydantic model to a dict, or {} for anything else."""
    dump = getattr(value, "model_dump", None)
    return dump() if callable(dump) else {}


def _node_update(node: str, update: dict) -> dict | None:
    """Curate a node's state update into a JSON-safe payload."""
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


class AgentEventStream:
    """Relay graph updates to a client, one node event per stage.

    The graph iterates inside a pump task, while the consumer drains a
    queue with per-iteration timeouts. Pings therefore fire on an idle
    queue instead of cancelling the in-flight graph run, and one outer
    timeout bounds total runtime.
    """

    def __init__(
        self,
        request: AlchemyRequest,
        *,
        timeout_seconds: int,
        ping_interval_seconds: float,
    ) -> None:
        self._initial_state = AgentState(request=request)
        self._timeout_seconds = timeout_seconds
        self._ping_interval_seconds = ping_interval_seconds

    async def events(self) -> AsyncIterator[str]:
        """Yield node events, an error event on failure, then done."""
        queue: asyncio.Queue = asyncio.Queue()
        stream_done = object()
        pump_task = asyncio.create_task(self._pump(queue, stream_done))
        try:
            try:
                async with asyncio.timeout(self._timeout_seconds):
                    async for event in self._drain(queue, stream_done):
                        yield event
                yield _sse_event("done", {})
            except TimeoutError:
                logger.warning("agent_stream_timeout")
                yield _sse_event(
                    "error", {"message": "Agent pipeline timed out"}
                )
            except Exception as exc:
                logger.exception("agent_stream_failed")
                yield _sse_event(
                    "error", {"message": f"{type(exc).__name__}: {exc}"}
                )
        finally:
            pump_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await pump_task

    async def _pump(self, queue: asyncio.Queue, stream_done: object) -> None:
        """Push graph chunks into the queue, sentinel token at the end."""
        try:
            async for chunk in agent_graph.astream(
                self._initial_state, stream_mode="updates"
            ):
                await queue.put(chunk)
        except Exception as exc:
            queue.put_nowait(exc)
        finally:
            queue.put_nowait(stream_done)

    async def _drain(
        self, queue: asyncio.Queue, stream_done: object
    ) -> AsyncIterator[str]:
        """Forward chunks as events; ping once per idle interval."""
        while True:
            try:
                async with asyncio.timeout(self._ping_interval_seconds):
                    item = await queue.get()
            except TimeoutError:
                yield ": ping\n\n"
                continue
            if item is stream_done:
                return
            if isinstance(item, BaseException):
                raise item
            if not isinstance(item, dict):
                continue
            for node, update in item.items():
                payload = _node_update(node, update)
                if payload:
                    yield _sse_event(
                        "node",
                        {"node": node, "stage": "end", "data": payload},
                    )

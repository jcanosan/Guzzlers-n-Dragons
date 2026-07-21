"""LangGraph: Planner → Creator → Critic with feedback loop."""

import structlog
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.agents.creator import run_creator
from src.agents.critic import run_critic
from src.agents.planner import run_planner
from src.schemas.agents import AgentState

logger = structlog.get_logger()

MAX_ITERATIONS = 3


def _should_continue(state: AgentState) -> str:
    """Decide whether to loop back to Planner or end the graph."""
    if state.iteration >= MAX_ITERATIONS:
        logger.info("agent_loop_max_iterations", iteration=state.iteration)
        return END

    report = state.report or {}
    if report.get("thematic_consistency") == "FAIL":
        logger.info("agent_loop_replan", iteration=state.iteration)
        return "planner"

    logger.info(
        "agent_loop_accepted", result=report.get("thematic_consistency")
    )
    return END


def build_graph() -> CompiledStateGraph:
    """Build the Planner → Creator → Critic LangGraph."""
    graph = StateGraph(AgentState)

    graph.add_node("planner", run_planner)
    graph.add_node("creator", run_creator)
    graph.add_node("critic", run_critic)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "creator")
    graph.add_edge("creator", "critic")
    graph.add_conditional_edges(
        "critic",
        _should_continue,
        {"planner": "planner", END: END},
    )

    return graph.compile()


# Module-level compiled graph
agent_graph: CompiledStateGraph = build_graph()

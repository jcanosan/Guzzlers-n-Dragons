"""Planner agent: extracts constraints, identifies techniques, plans needs."""

import structlog

from src.agents.llm import call_llm
from src.schemas.agents import AgentState, PlannerResult
from src.services.database import (
    get_ingredient_by_name,
    get_pattern_by_meal_type,
)
from src.tools.cooking import find_technique_substitution

logger = structlog.get_logger()

PLANNER_SYSTEM_PROMPT = (
    "You are a culinary Planner agent. Given a fictional ingredient and"
    " constraints, determine:\n"
    "1. Required cooking techniques for this meal type\n"
    "2. The dominant flavor profile to maintain\n"
    "3. Texture goals to achieve\n"
    "4. Key knowledge queries the Creator agent should run\n\n"
    "Output ONLY valid JSON matching the PlannerResult schema:\n"
    "{\n"
    '  "technique_requirements": ["string"],\n'
    '  "flavor_profile": {"sweet": 0.5, "umami": 0.3},\n'
    '  "texture_goals": ["string"],\n'
    '  "constraint_summary": "string",\n'
    '  "knowledge_queries": ["string"]\n'
    "}\n\n"
    "Rules:\n"
    "- Respect the thematic group's technology level\n"
    "- Technique requirements must be concrete (e.g. 'emulsify', 'sauté')\n"
    "- Knowledge queries should be like 'flavor pairing for saffron'\n"
    "- Constraint summary is one sentence describing the user's limitations"
)


def _gather_context(state: AgentState) -> dict:
    """Query DB and RAG for ingredient profile, pattern, and technique docs."""
    request = state.request
    ingredient_name = request.fictional_ingredient

    ingredient_profile = get_ingredient_by_name(ingredient_name)
    pattern = get_pattern_by_meal_type(request.meal_type)

    rag_context = []
    for query in [
        f"basic techniques for {request.meal_type}",
        f"cooking methods for {request.meal_type} recipe",
    ]:
        results = find_technique_substitution(query)
        if results:
            rag_context.append(results[0]["content"])

    return {
        "request": request,
        "ingredient_name": ingredient_name,
        "ingredient_profile": ingredient_profile,
        "pattern": pattern,
        "rag_context": rag_context,
    }


def _build_prompt(state: AgentState, ctx: dict) -> str:
    """Build the user prompt string for the Planner LLM call."""
    request = ctx["request"]
    profile = ctx["ingredient_profile"]
    pattern = ctx["pattern"]

    return (
        f"Fictional Ingredient: {ctx['ingredient_name']}\n"
        f"Thematic Group: {request.thematic_group}\n"
        f"Meal Type: {request.meal_type}\n"
        f"Constraints: servings={request.constraints.servings},"
        f" max_prep={request.constraints.max_prep_time_minutes}min,"
        f" max_cook={request.constraints.max_cook_time_minutes}min,"
        f" dietary={request.constraints.dietary},"
        f" equipment={request.constraints.equipment},"
        f" difficulty={request.constraints.difficulty}\n\n"
        f"Ingredient Lore:"
        f" {profile.description if profile else 'Unknown'}\n"
        f"Taste Profile:"
        f" {profile.taste_profile if profile else {}}\n"
        f"Texture: {profile.texture if profile else 'Unknown'}\n"
        f"Magical Properties:"
        f" {profile.magical_properties if profile else 'None'}\n"
        f"Real-World Approximations:"
        f" {profile.real_world_approximations if profile else []}\n\n"
        f"Recipe Pattern Template:"
        f" {pattern.pattern_json if pattern else 'No template found'}\n\n"
        f"RAG Cooking Techniques: {ctx['rag_context']}\n"
    )


def _parse_response(content: str) -> PlannerResult:
    """Parse the LLM response into a PlannerResult."""
    import json

    try:
        data = json.loads(content)
        return PlannerResult(**data)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("planner_parse_failed", error=str(exc))
        return PlannerResult()


async def run_planner(state: AgentState) -> dict:
    """Execute the Planner agent node.

    Gathers context, calls the LLM, and returns PlannerResult.
    """
    ctx = _gather_context(state)
    user_prompt = _build_prompt(state, ctx)
    response = await call_llm(PLANNER_SYSTEM_PROMPT, user_prompt)
    planner_result = _parse_response(str(response.content))

    logger.info(
        "planner_completed",
        ingredient=ctx["ingredient_name"],
        techniques=planner_result.technique_requirements,
    )

    return {
        "ingredient_profile": ctx["ingredient_profile"],
        "planner_result": planner_result,
    }

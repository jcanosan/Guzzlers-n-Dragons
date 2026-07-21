"""Creator agent: generates novel recipes with LLM + structured knowledge."""

import json

import structlog

from src.agents.llm import call_llm
from src.schemas.agents import AgentState, DraftRecipe, PlannerResult
from src.tools.agent_tools import find_recipes_by_ingredient
from src.tools.cooking import (
    find_flavor_pairing,
    find_technique_substitution,
    find_texture_modification,
)

logger = structlog.get_logger()

CREATOR_SYSTEM_PROMPT = (
    "You are a culinary Creator agent. Given a fictional ingredient, its"
    " lore, RAG cooking science, and real-world recipe patterns, generate a"
    " plausible, cookable recipe.\n\n"
    "Output ONLY valid JSON matching:\n"
    "{\n"
    '  "name": "string",\n'
    '  "description": "string",\n'
    '  "ingredients": [{"item": "string", "amount": "string",'
    ' "notes": "string"}],\n'
    '  "instructions": ["string"],\n'
    '  "prep_time_minutes": int,\n'
    '  "cook_time_minutes": int,\n'
    '  "servings": int,\n'
    '  "difficulty": "easy|medium|hard",\n'
    '  "plausibility_notes": ["string"]\n'
    "}\n\n"
    "Rules:\n"
    "- Respect the thematic group — no modern ingredients in high fantasy\n"
    "- Use real-world approximations for the fictional ingredient\n"
    "- Instructions must be concrete and cookable\n"
    "- Cooking techniques should match RAG recommendations\n"
    "- Times must fit within user constraints"
)


async def _gather_rag_context(
    planner, ingredient, ingredient_name: str
) -> dict:
    """Query RAG tools for technique, flavor, and texture context."""
    technique_docs = []
    for query in planner.knowledge_queries[:3]:
        results = find_technique_substitution(query)
        if results:
            technique_docs.append(results[0]["content"])

    approx = (
        ingredient.real_world_approximations[0]["ingredient"]
        if ingredient and ingredient.real_world_approximations
        else ingredient_name
    )

    flavor_docs = []
    flavor_results = find_flavor_pairing(approx)
    if flavor_results:
        flavor_docs.append(flavor_results[0]["content"])

    texture_docs = []
    texture_start = ingredient.texture if ingredient else "unknown"
    texture_results = find_texture_modification("desired", texture_start)
    if texture_results:
        texture_docs.append(texture_results[0]["content"])

    return {
        "technique_docs": technique_docs,
        "flavor_docs": flavor_docs,
        "texture_docs": texture_docs,
        "approx_ingredient": approx,
    }


async def _gather_meal_patterns(approx_ingredient: str) -> str:
    """Fetch real-world recipe patterns from TheMealDB."""
    meal_patterns = await find_recipes_by_ingredient.ainvoke(
        {"ingredient": approx_ingredient}
    )
    return json.dumps(meal_patterns[:3], indent=2)


def _build_prompt(
    state: AgentState,
    planner: PlannerResult,
    rag: dict,
    pattern_context: str,
) -> str:
    """Build the user prompt string for the Creator LLM call."""
    request = state.request
    ingredient = state.ingredient_profile

    lore = ingredient.description if ingredient else "Unknown"
    taste = ingredient.taste_profile if ingredient else {}
    texture = ingredient.texture if ingredient else "Unknown"
    approx = ingredient.real_world_approximations if ingredient else []

    return (
        f"Fictional Ingredient: {request.fictional_ingredient}\n"
        f"Thematic Group: {request.thematic_group}\n"
        f"Meal Type: {request.meal_type}\n\n"
        f"Constraints:\n"
        f"- Servings: {request.constraints.servings}\n"
        f"- Max Prep: {request.constraints.max_prep_time_minutes} min\n"
        f"- Max Cook: {request.constraints.max_cook_time_minutes} min\n"
        f"- Dietary: {request.constraints.dietary}\n"
        f"- Equipment: {request.constraints.equipment}\n"
        f"- Difficulty: {request.constraints.difficulty}\n\n"
        f"Planner Output:\n"
        f"- Techniques: {planner.technique_requirements}\n"
        f"- Flavor: {planner.flavor_profile}\n"
        f"- Texture Goals: {planner.texture_goals}\n"
        f"- Summary: {planner.constraint_summary}\n\n"
        f"Ingredient Lore:\n"
        f"- Description: {lore}\n"
        f"- Taste: {taste}\n"
        f"- Texture: {texture}\n"
        f"- Approximations: {approx}\n\n"
        f"RAG Technique Docs: {rag['technique_docs'][:2]}\n"
        f"RAG Flavor Docs: {rag['flavor_docs'][:1]}\n"
        f"RAG Texture Docs: {rag['texture_docs'][:1]}\n\n"
        f"TheMealDB Patterns:\n{pattern_context}\n"
    )


def _parse_response(content: str) -> DraftRecipe:
    """Parse the LLM response into a DraftRecipe."""
    try:
        data = json.loads(content)
        return DraftRecipe(**data)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("creator_parse_failed", error=str(exc))
        return DraftRecipe()


async def run_creator(state: AgentState) -> dict:
    """Execute the Creator agent node.

    Gathers RAG context and TheMealDB patterns, calls the LLM,
    and returns a draft recipe.
    """
    planner = state.planner_result
    if not planner:
        logger.warning("creator_skipped", reason="no_planner_result")
        return {"draft_recipe": DraftRecipe()}

    ingredient = state.ingredient_profile
    ingredient_name = state.request.fictional_ingredient

    rag = await _gather_rag_context(planner, ingredient, ingredient_name)
    pattern_context = await _gather_meal_patterns(rag["approx_ingredient"])
    user_prompt = _build_prompt(state, planner, rag, pattern_context)

    response = await call_llm(CREATOR_SYSTEM_PROMPT, user_prompt)
    draft = _parse_response(str(response.content))

    logger.info("creator_completed", recipe_name=draft.name)
    return {"draft_recipe": draft}

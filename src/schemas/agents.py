"""Intermediate schemas exchanged between LangGraph agent nodes."""

from pydantic import BaseModel, Field

from src.schemas.domain import FictionalIngredient
from src.schemas.request import AlchemyRequest


class PlannerResult(BaseModel):
    """Output from Planner: techniques, flavor, texture, knowledge needs."""

    technique_requirements: list[str] = Field(
        description="Cooking techniques required for this meal type",
        default_factory=list,
    )
    flavor_profile: dict = Field(
        description="Taste profile of the fictional ingredient",
        default_factory=dict,
    )
    texture_goals: list[str] = Field(
        description="Target textures to achieve in the final recipe",
        default_factory=list,
    )
    constraint_summary: str = Field(
        description="Human-readable summary of user constraints",
        default="",
    )
    knowledge_queries: list[str] = Field(
        description="Search queries the Creator should run against RAG/APIs",
        default_factory=list,
    )


class DraftRecipe(BaseModel):
    """Recipe draft produced by the Creator, before Critic validation.

    Mirrors Recipe from response.py but includes the Creator's own
    plausibility notes about decisions made during generation.
    """

    name: str = ""
    description: str = ""
    ingredients: list[dict] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)
    prep_time_minutes: int = 0
    cook_time_minutes: int = 0
    servings: int = 4
    difficulty: str = Field(pattern="^(easy|medium|hard)$", default="medium")
    plausibility_notes: list[str] = Field(
        description="Creator's notes about its own reasoning and choices",
        default_factory=list,
    )


class AgentState(BaseModel):
    """State that flows through the Planner → Creator → Critic LangGraph."""

    request: AlchemyRequest
    ingredient_profile: FictionalIngredient | None = None
    planner_result: PlannerResult | None = None
    draft_recipe: DraftRecipe | None = None
    report: dict | None = Field(
        description="PlausibilityReport as dict for LangGraph compat",
        default=None,
    )
    iteration: int = Field(
        default=0, description="Current feedback loop iteration"
    )

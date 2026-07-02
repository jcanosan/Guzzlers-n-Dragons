from enum import StrEnum

from pydantic import BaseModel, Field


class ValidationSeverity(StrEnum):
    """Severity level for a validation issue."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ValidationIssue(BaseModel):
    """A single validation problem flagged by the Critic agent."""

    type: str
    severity: ValidationSeverity
    message: str
    suggestion: str | None = None


class SubstitutionOption(BaseModel):
    """One suggested swap for a hard-to-source ingredient."""

    item: str
    reasoning: str


class Substitution(BaseModel):
    """List of viable substitutes for a given ingredient."""

    for_ingredient: str = Field(alias="for")
    options: list[SubstitutionOption]


class NutritionEstimate(BaseModel):
    """Per-serving macros from USDA data lookup."""

    calories_per_serving: float | None = None
    protein_g: float | None = None
    carbs_g: float | None = None
    fat_g: float | None = None
    notes: str = ""


class PlausibilityReport(BaseModel):
    """Critic output: thematic, nutritional, and substitution checks."""

    thematic_consistency: str = Field(pattern="^(PASS|WARN|FAIL)$")
    notes: list[str] = Field(default_factory=list)
    substitutions: list[Substitution] = Field(default_factory=list)
    nutrition_estimate: NutritionEstimate = Field(
        default_factory=NutritionEstimate
    )
    validation_issues: list[ValidationIssue] = Field(default_factory=list)


class Recipe(BaseModel):
    """A final cookable recipe with ingredients, steps, and metadata."""

    name: str
    description: str
    ingredients: list[dict]
    instructions: list[str]
    prep_time_minutes: int
    cook_time_minutes: int
    servings: int
    difficulty: str = Field(pattern="^(easy|medium|hard)$")


class AlchemyResult(BaseModel):
    """Top-level response from the recipe-alchemy pipeline."""

    recipe: Recipe
    plausibility_report: PlausibilityReport
    metadata: dict = Field(default_factory=dict)

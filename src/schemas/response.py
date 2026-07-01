from enum import StrEnum

from pydantic import BaseModel, Field


class ValidationSeverity(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ValidationIssue(BaseModel):
    type: str
    severity: ValidationSeverity
    message: str
    suggestion: str | None = None


class SubstitutionOption(BaseModel):
    item: str
    reasoning: str


class Substitution(BaseModel):
    for_ingredient: str = Field(alias="for")
    options: list[SubstitutionOption]


class NutritionEstimate(BaseModel):
    calories_per_serving: float | None = None
    protein_g: float | None = None
    carbs_g: float | None = None
    fat_g: float | None = None
    notes: str = ""


class PlausibilityReport(BaseModel):
    thematic_consistency: str = Field(pattern="^(PASS|WARN|FAIL)$")
    notes: list[str] = Field(default_factory=list)
    substitutions: list[Substitution] = Field(default_factory=list)
    nutrition_estimate: NutritionEstimate = Field(
        default_factory=NutritionEstimate
    )
    validation_issues: list[ValidationIssue] = Field(default_factory=list)


class Recipe(BaseModel):
    name: str
    description: str
    ingredients: list[dict]  # {"item": str, "amount": str, "notes": str}
    instructions: list[str]
    prep_time_minutes: int
    cook_time_minutes: int
    servings: int
    difficulty: str = Field(pattern="^(easy|medium|hard)$")


class AlchemyResult(BaseModel):
    recipe: Recipe
    plausibility_report: PlausibilityReport
    metadata: dict = Field(default_factory=dict)

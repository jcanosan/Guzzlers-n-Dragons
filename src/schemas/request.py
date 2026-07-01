from pydantic import BaseModel, Field


class Constraints(BaseModel):
    servings: int = Field(default=4, ge=1, le=50)
    max_prep_time_minutes: int = Field(default=60, ge=5, le=480)
    dietary: list[str] = Field(default_factory=list)
    equipment: list[str] = Field(default_factory=list)
    max_cook_time_minutes: int = Field(default=120, ge=0, le=720)
    difficulty: str | None = Field(default=None, pattern="^(easy|medium|hard)$")


class AlchemyRequest(BaseModel):
    fictional_ingredient: str = Field(..., min_length=1, max_length=100)
    meal_type: str = Field(..., min_length=1, max_length=50)
    thematic_group: str = Field(
        ..., pattern="^(high_fantasy|sci_fi|mythological)$"
    )
    constraints: Constraints = Field(default_factory=Constraints)

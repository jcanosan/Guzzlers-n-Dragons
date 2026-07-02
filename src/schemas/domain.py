from pydantic import BaseModel, Field


class FictionalIngredient(BaseModel):
    """A fictional ingredient from a game/movie universe."""

    id: int | None = None
    name: str
    description: str
    thematic_group: str
    taste_profile: dict = Field(default_factory=dict)
    texture: str
    rarity: str = Field(pattern="^(common|rare|legendary)$")
    magical_properties: str = ""
    preparation_notes: str = ""
    real_world_approximations: list[dict] = Field(default_factory=list)


class RealIngredient(BaseModel):
    """A real-world ingredient with optional USDA nutrition data."""

    id: int | None = None
    name: str
    usda_fdc_id: int | None = None
    category: str = ""
    nutrition_per_100g: dict = Field(default_factory=dict)


class RecipePattern(BaseModel):
    """A parameterized recipe template classified by meal type."""

    id: int | None = None
    meal_type: str
    pattern_json: dict
    example_ingredients: list[str] = Field(default_factory=list)

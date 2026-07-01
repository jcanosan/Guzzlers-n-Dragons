from pydantic import BaseModel, Field


class FictionalIngredient(BaseModel):
    id: int | None = None
    name: str
    description: str
    thematic_group: str
    taste_profile: dict = Field(
        default_factory=dict
    )  # {"sweet": 0.2, "umami": 0.8, ...}
    texture: str
    rarity: str = Field(pattern="^(common|rare|legendary)$")
    magical_properties: str = ""
    preparation_notes: str = ""
    real_world_approximations: list[dict] = Field(
        default_factory=list
    )  # [{"ingredient": "...", "reasoning": "..."}]


class RealIngredient(BaseModel):
    id: int | None = None
    name: str
    usda_fdc_id: int | None = None
    category: str = ""
    nutrition_per_100g: dict = Field(default_factory=dict)


class RecipePattern(BaseModel):
    id: int | None = None
    meal_type: str
    pattern_json: dict  # Parameterized template structure
    example_ingredients: list[str] = Field(default_factory=list)

import pytest
from pydantic import ValidationError

from src.schemas.domain import (
    FictionalIngredient,
    RealIngredient,
    RecipePattern,
)


class TestFictionalIngredient:
    def test_valid_minimal(self):
        ingredient = FictionalIngredient(
            name="test",
            description="desc",
            thematic_group="fantasy",
            texture="soft",
            rarity="common",
        )
        assert ingredient.name == "test"
        assert ingredient.rarity == "common"

    def test_valid_full(self, fictional_ingredient_data):
        ingredient = FictionalIngredient(**fictional_ingredient_data)
        assert ingredient.name == "test_ingredient"
        assert ingredient.rarity == "rare"

    def test_invalid_rarity(self):
        with pytest.raises(ValidationError):
            FictionalIngredient(
                name="test",
                description="desc",
                thematic_group="fantasy",
                texture="soft",
                rarity="invalid",
            )

    def test_missing_required_args(self):
        with pytest.raises(ValidationError):
            FictionalIngredient(name="test")  # type: ignore

    def test_defaults(self):
        ingredient = FictionalIngredient(
            name="test",
            description="desc",
            thematic_group="fantasy",
            texture="soft",
            rarity="common",
        )
        assert ingredient.taste_profile == {}
        assert ingredient.real_world_approximations == []
        assert ingredient.magical_properties == ""
        assert ingredient.preparation_notes == ""

    def test_approximations(self):
        ingredient = FictionalIngredient(
            name="test",
            description="desc",
            thematic_group="fantasy",
            texture="soft",
            rarity="common",
            real_world_approximations=[
                {"ingredient": "flour", "reasoning": "common sub"}
            ],
        )
        assert len(ingredient.real_world_approximations) == 1


class TestRealIngredient:
    def test_valid_minimal(self):
        ingredient = RealIngredient(name="salt")
        assert ingredient.name == "salt"
        assert ingredient.usda_fdc_id is None

    def test_valid_full(self, real_ingredient_data):
        ingredient = RealIngredient(**real_ingredient_data)
        assert ingredient.usda_fdc_id == 12345

    def test_nutrition_defaults(self):
        ingredient = RealIngredient(name="water")
        assert ingredient.nutrition_per_100g == {}

    def test_missing_name(self):
        with pytest.raises(ValidationError):
            RealIngredient()  # type: ignore


class TestRecipePattern:
    def test_valid_minimal(self):
        pattern = RecipePattern(
            meal_type="stew", pattern_json={"base": "broth"}
        )
        assert pattern.meal_type == "stew"

    def test_valid_full(self):
        pattern = RecipePattern(
            meal_type="dessert",
            pattern_json={"base": "cake", "sweetener": "sugar"},
            example_ingredients=["flour", "sugar"],
        )
        assert len(pattern.example_ingredients) == 2

    def test_missing_required_args(self):
        with pytest.raises(ValidationError):
            RecipePattern(meal_type="soup")  # type: ignore

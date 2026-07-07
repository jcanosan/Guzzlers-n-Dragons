import pytest
from pydantic import ValidationError

from src.schemas.domain import (
    FictionalIngredient,
    RealIngredient,
    RecipePattern,
)


class TestFictionalIngredient:
    def test_valid_minimal(self):
        ing = FictionalIngredient(
            name="test",
            description="desc",
            thematic_group="fantasy",
            texture="soft",
            rarity="common",
        )
        assert ing.name == "test"
        assert ing.rarity == "common"

    def test_valid_full(self, fictional_ingredient_data):
        ing = FictionalIngredient(**fictional_ingredient_data)
        assert ing.name == "test_ingredient"
        assert ing.rarity == "rare"

    def test_invalid_rarity(self):
        with pytest.raises(ValidationError):
            FictionalIngredient(
                name="test",
                description="desc",
                thematic_group="fantasy",
                texture="soft",
                rarity="invalid",
            )

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            FictionalIngredient(name="test")  # type: ignore

    def test_defaults(self):
        ing = FictionalIngredient(
            name="test",
            description="desc",
            thematic_group="fantasy",
            texture="soft",
            rarity="common",
        )
        assert ing.taste_profile == {}
        assert ing.real_world_approximations == []
        assert ing.magical_properties == ""
        assert ing.preparation_notes == ""

    def test_approximations(self):
        ing = FictionalIngredient(
            name="test",
            description="desc",
            thematic_group="fantasy",
            texture="soft",
            rarity="common",
            real_world_approximations=[
                {"ingredient": "flour", "reasoning": "common sub"}
            ],
        )
        assert len(ing.real_world_approximations) == 1


class TestRealIngredient:
    def test_valid_minimal(self):
        ing = RealIngredient(name="salt")
        assert ing.name == "salt"
        assert ing.usda_fdc_id is None

    def test_valid_full(self, real_ingredient_data):
        ing = RealIngredient(**real_ingredient_data)
        assert ing.usda_fdc_id == 12345

    def test_nutrition_defaults(self):
        ing = RealIngredient(name="water")
        assert ing.nutrition_per_100g == {}

    def test_missing_name(self):
        with pytest.raises(ValidationError):
            RealIngredient()  # type: ignore


class TestRecipePattern:
    def test_valid_minimal(self):
        pat = RecipePattern(meal_type="stew", pattern_json={"base": "broth"})
        assert pat.meal_type == "stew"

    def test_valid_full(self):
        pat = RecipePattern(
            meal_type="dessert",
            pattern_json={"base": "cake", "sweetener": "sugar"},
            example_ingredients=["flour", "sugar"],
        )
        assert len(pat.example_ingredients) == 2

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            RecipePattern(meal_type="soup")  # type: ignore

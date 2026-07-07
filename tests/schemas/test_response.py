import pytest
from pydantic import ValidationError

from src.schemas.response import (
    AlchemyResult,
    NutritionEstimate,
    PlausibilityReport,
    Recipe,
    Substitution,
    SubstitutionOption,
    ValidationIssue,
    ValidationSeverity,
)


class TestValidationSeverity:
    def test_values(self):
        assert ValidationSeverity.HIGH == "HIGH"
        assert ValidationSeverity.MEDIUM == "MEDIUM"
        assert ValidationSeverity.LOW == "LOW"


class TestValidationIssue:
    def test_valid_minimal(self):
        issue = ValidationIssue(
            type="test", severity=ValidationSeverity.HIGH, message="bad"
        )
        assert issue.type == "test"
        assert issue.suggestion is None

    def test_valid_with_suggestion(self):
        issue = ValidationIssue(
            type="test",
            severity=ValidationSeverity.LOW,
            message="bad",
            suggestion="do this instead",
        )
        assert issue.suggestion == "do this instead"


class TestSubstitutionOption:
    def test_valid(self):
        option = SubstitutionOption(item="flour", reasoning="common thickener")
        assert option.item == "flour"


class TestSubstitution:
    def test_valid(self):
        substitution = Substitution.model_validate(
            {
                "for": "butter",
                "options": [{"item": "oil", "reasoning": "vegan option"}],
            }
        )
        assert substitution.for_ingredient == "butter"
        assert len(substitution.options) == 1


class TestNutritionEstimate:
    def test_defaults(self):
        nutrition = NutritionEstimate()
        assert nutrition.calories_per_serving is None
        assert nutrition.protein_g is None
        assert nutrition.notes == ""

    def test_valid_full(self):
        nutrition = NutritionEstimate(
            calories_per_serving=500, protein_g=20, carbs_g=60, fat_g=15
        )
        assert nutrition.calories_per_serving == 500


class TestPlausibilityReport:
    def test_defaults(self):
        report = PlausibilityReport(thematic_consistency="PASS")
        assert report.thematic_consistency == "PASS"
        assert report.notes == []
        assert report.substitutions == []

    def test_invalid_consistency(self):
        with pytest.raises(ValidationError):
            PlausibilityReport(thematic_consistency="MAYBE")


class TestRecipe:
    def test_valid_minimal(self):
        recipe = Recipe(
            name="test",
            description="desc",
            ingredients=[{"item": "flour", "amount": "2 cups"}],
            instructions=["mix", "bake"],
            prep_time_minutes=10,
            cook_time_minutes=30,
            servings=4,
            difficulty="easy",
        )
        assert recipe.name == "test"

    def test_invalid_difficulty(self):
        with pytest.raises(ValidationError):
            Recipe(
                name="test",
                description="desc",
                ingredients=[],
                instructions=[],
                prep_time_minutes=0,
                cook_time_minutes=0,
                servings=1,
                difficulty="extreme",
            )


class TestAlchemyResult:
    def test_valid(self):
        result = AlchemyResult(
            recipe=Recipe(
                name="test",
                description="desc",
                ingredients=[],
                instructions=[],
                prep_time_minutes=5,
                cook_time_minutes=10,
                servings=2,
                difficulty="easy",
            ),
            plausibility_report=PlausibilityReport(thematic_consistency="PASS"),
        )
        assert result.recipe.name == "test"
        assert result.metadata == {}

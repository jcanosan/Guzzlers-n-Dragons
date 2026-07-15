import pytest
from pydantic import ValidationError

from src.schemas.request import AlchemyRequest, Constraints


class TestConstraints:
    def test_defaults(self):
        c = Constraints()
        assert c.servings == 4
        assert c.max_prep_time_minutes == 60
        assert c.dietary == []
        assert c.equipment == []
        assert c.difficulty is None

    def test_valid_custom(self):
        c = Constraints(servings=2, max_prep_time_minutes=30, difficulty="easy")
        assert c.servings == 2
        assert c.difficulty == "easy"

    def test_invalid_servings(self):
        with pytest.raises(ValidationError):
            Constraints(servings=0)

    def test_invalid_servings_too_high(self):
        with pytest.raises(ValidationError):
            Constraints(servings=100)

    def test_invalid_difficulty(self):
        with pytest.raises(ValidationError):
            Constraints(difficulty="expert")


class TestAlchemyRequest:
    def test_valid(self):
        request = AlchemyRequest(
            fictional_ingredient="lembas",
            meal_type="bread",
            thematic_group="high_fantasy",
        )
        assert request.fictional_ingredient == "lembas"
        assert isinstance(request.constraints, Constraints)

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            AlchemyRequest(fictional_ingredient="lembas")  # type: ignore

    def test_invalid_thematic_group(self):
        with pytest.raises(ValidationError):
            AlchemyRequest(
                fictional_ingredient="lembas",
                meal_type="bread",
                thematic_group="cyberpunk",
            )

    def test_empty_ingredient(self):
        with pytest.raises(ValidationError):
            AlchemyRequest(
                fictional_ingredient="",
                meal_type="bread",
                thematic_group="high_fantasy",
            )

from typing import Any

from src.schemas.domain import (
    FictionalIngredient,
    RealIngredient,
    RecipePattern,
)
from src.services import database as db


def _init_test_db(monkeypatch):
    monkeypatch.setattr(db.settings, "database_url", "sqlite://")
    db.init_db()


_MINIMAL_ING: dict[str, Any] = {
    "description": "",
    "thematic_group": "fantasy",
    "texture": "",
    "rarity": "common",
}


_SHARED_ARGS: dict[str, Any] = {
    "description": "",
    "texture": "",
    "rarity": "common",
}


class TestGetIngredientByName:
    def test_not_found(self, monkeypatch):
        _init_test_db(monkeypatch)
        result = db.get_ingredient_by_name("nonexistent")
        assert result is None

    def test_found(self, monkeypatch):
        _init_test_db(monkeypatch)
        ing = FictionalIngredient(name="test_item", **_MINIMAL_ING)
        db.seed_fictional_ingredients([ing])

        result = db.get_ingredient_by_name("test_item")
        assert result is not None
        assert result.name == "test_item"

    def test_null_fields(self, monkeypatch):
        _init_test_db(monkeypatch)
        from src.services.database import FictionalIngredientORM

        sess = db.get_session()
        orm = FictionalIngredientORM(
            name="null_item",
            description=None,
            thematic_group="fantasy",
            texture=None,
        )
        sess.add(orm)
        sess.commit()
        sess.close()

        result = db.get_ingredient_by_name("null_item")
        assert result is not None
        assert result.description == ""
        assert result.texture == ""


class TestListIngredients:
    def test_empty(self, monkeypatch):
        _init_test_db(monkeypatch)
        results = db.list_ingredients()
        assert results == []

    def test_all(self, monkeypatch):
        _init_test_db(monkeypatch)
        db.seed_fictional_ingredients(
            [
                FictionalIngredient(name="a", **_MINIMAL_ING),
                FictionalIngredient(name="b", **_MINIMAL_ING),
            ]
        )
        results = db.list_ingredients()
        assert len(results) == 2

    def test_filter_by_group(self, monkeypatch):
        _init_test_db(monkeypatch)
        db.seed_fictional_ingredients(
            [
                FictionalIngredient(name="a", **_MINIMAL_ING),
                FictionalIngredient(
                    name="b", **_SHARED_ARGS, thematic_group="sci_fi"
                ),
            ]
        )
        results = db.list_ingredients(thematic_group="fantasy")
        assert len(results) == 1
        assert results[0].name == "a"


class TestSeedFictionalIngredients:
    def test_seed_new(self, monkeypatch):
        _init_test_db(monkeypatch)
        ingredients = [FictionalIngredient(name="new_item", **_MINIMAL_ING)]
        count = db.seed_fictional_ingredients(ingredients)
        assert count == 1

    def test_seed_duplicate(self, monkeypatch):
        _init_test_db(monkeypatch)
        ing = FictionalIngredient(name="dup", **_MINIMAL_ING)
        db.seed_fictional_ingredients([ing])
        count = db.seed_fictional_ingredients([ing])
        assert count == 0

    def test_seed_multiple(self, monkeypatch):
        _init_test_db(monkeypatch)
        ingredients = [
            FictionalIngredient(name="a", **_MINIMAL_ING),
            FictionalIngredient(name="b", **_MINIMAL_ING),
        ]
        count = db.seed_fictional_ingredients(ingredients)
        assert count == 2


class TestSeedRealIngredients:
    def test_seed_new(self, monkeypatch):
        _init_test_db(monkeypatch)
        ingredients = [RealIngredient(name="salt", usda_fdc_id=1)]
        count = db.seed_real_ingredients(ingredients)
        assert count == 1

    def test_seed_duplicate(self, monkeypatch):
        _init_test_db(monkeypatch)
        ing = RealIngredient(name="salt", usda_fdc_id=1)
        db.seed_real_ingredients([ing])
        count = db.seed_real_ingredients([ing])
        assert count == 0


class TestSeedRecipePatterns:
    def test_seed_new(self, monkeypatch):
        _init_test_db(monkeypatch)
        patterns = [
            RecipePattern(meal_type="test", pattern_json={"key": "val"})
        ]
        count = db.seed_recipe_patterns(patterns)
        assert count == 1

    def test_seed_duplicate(self, monkeypatch):
        _init_test_db(monkeypatch)
        pat = RecipePattern(meal_type="test", pattern_json={"key": "val"})
        db.seed_recipe_patterns([pat])
        count = db.seed_recipe_patterns([pat])
        assert count == 0

"""Shared fixtures for tests."""

import pytest


@pytest.fixture
def fictional_ingredient_data() -> dict:
    return {
        "name": "test_ingredient",
        "description": "A test ingredient",
        "thematic_group": "high_fantasy",
        "taste_profile": {"sweet": 0.5, "savory": 0.5},
        "texture": "creamy",
        "rarity": "rare",
        "magical_properties": "Glows in the dark",
        "preparation_notes": "Handle with care",
        "real_world_approximations": [
            {"ingredient": "test_item", "reasoning": "test_reason"}
        ],
    }


@pytest.fixture
def real_ingredient_data() -> dict:
    return {
        "name": "test_real",
        "usda_fdc_id": 12345,
        "category": "test",
        "nutrition_per_100g": {"calories": 100, "protein": 5},
    }

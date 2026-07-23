"""Shared fixtures for tests."""

import sys

import pytest

from tests.mock_embeddings import MockEmbeddings


@pytest.fixture(autouse=True, scope="session")
def mock_ollama_embeddings():
    """Replace OllamaEmbeddings with all-zero vectors across all tests.

    Prevents every test from needing a running Ollama instance for
    embedding calls (nomic-embed-text). Applied once per session.
    """
    with pytest.MonkeyPatch.context() as m:
        m.setattr(
            sys.modules["src.services.vector_store"],
            "OllamaEmbeddings",
            MockEmbeddings,
        )
        yield


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

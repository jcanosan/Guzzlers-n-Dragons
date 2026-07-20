"""Tests for agent tool input validation."""

import pytest

from src.tools.validation import (
    MAX_INGREDIENT_LENGTH,
    InvalidIngredientError,
    validate_ingredient,
)


class TestValidateIngredient:
    def test_normal_name(self):
        assert validate_ingredient("chicken breast") == "chicken breast"

    def test_strips_whitespace(self):
        assert validate_ingredient("  apple  ") == "apple"

    def test_allows_punctuation(self):
        assert validate_ingredient("apple, with-seeds") == "apple, with-seeds"

    def test_rejects_empty(self):
        with pytest.raises(InvalidIngredientError, match="empty"):
            validate_ingredient("")

    def test_rejects_whitespace_only(self):
        with pytest.raises(InvalidIngredientError, match="empty"):
            validate_ingredient("   ")

    def test_rejects_too_long(self):
        name = "a" * (MAX_INGREDIENT_LENGTH + 1)
        with pytest.raises(InvalidIngredientError, match="exceeds"):
            validate_ingredient(name)

    def test_rejects_disallowed_chars(self):
        with pytest.raises(InvalidIngredientError, match="disallowed"):
            validate_ingredient("apple<script>")

    def test_rejects_path_injection(self):
        with pytest.raises(InvalidIngredientError, match="disallowed"):
            validate_ingredient("../etc/passwd")

    def test_rejects_sql_injection(self):
        with pytest.raises(InvalidIngredientError, match="disallowed"):
            validate_ingredient("'; DROP TABLE--")

    def test_max_length_accepted(self):
        name = "a" * MAX_INGREDIENT_LENGTH
        assert validate_ingredient(name) == name

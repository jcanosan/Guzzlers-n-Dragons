"""Input validation for agent tool inputs.

Charset-allowlist + length cap to mitigate request amplification and
clamping of external API query strings. User-supplied strings flow
into outbound HTTP calls (USDA, Fineli, Open Food Facts, TheMealDB);
reject them here to prevent abuse.
"""

import re

MAX_INGREDIENT_LENGTH = 100
_VALID_PATTERN = re.compile(r"^[\w\s'.,\-]+$")


class InvalidIngredientError(ValueError):
    """Raised when an ingredient name fails validation."""


def validate_ingredient(name: str) -> str:
    """Validate an ingredient name before it reaches outbound HTTP.

    Args:
        name: Ingredient name to validate.

    Returns:
        The trimmed name if valid.

    Raises:
        InvalidIngredientError: If the name is empty, too long, or
            contains characters outside the allowlist.
    """
    if not name or not name.strip():
        raise InvalidIngredientError("ingredient name cannot be empty")
    trimmed = name.strip()
    if len(trimmed) > MAX_INGREDIENT_LENGTH:
        raise InvalidIngredientError(
            f"ingredient name exceeds {MAX_INGREDIENT_LENGTH} chars"
        )
    if not _VALID_PATTERN.match(trimmed):
        raise InvalidIngredientError(
            "ingredient name contains disallowed characters"
        )
    return trimmed

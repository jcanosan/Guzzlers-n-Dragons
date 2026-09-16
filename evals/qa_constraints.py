"""Servings/time-limit constraint assertion.

Compares the final recipe against the pipeline's own Constraints
(echoed in the output as `constraints`): servings must match exactly and
prep/cook minutes must fit the limits passed to the pipeline.
"""

import json


def get_assert(output: str, context: dict) -> bool:
    try:
        result = json.loads(output)
        recipe = result["recipe"]
        want = result["constraints"]
    except TypeError, ValueError, KeyError:
        return False
    if not recipe:
        return False
    if recipe.get("servings") != want.get("servings"):
        return False
    for time_key, limit_key in (
        ("prep_time_minutes", "max_prep_time_minutes"),
        ("cook_time_minutes", "max_cook_time_minutes"),
    ):
        minutes = recipe.get(time_key)
        if not isinstance(minutes, int) or minutes > want.get(limit_key, 0):
            return False
    return True

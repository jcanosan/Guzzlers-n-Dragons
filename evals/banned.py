"""Recipe-only banned-ingredient assertion.

Checks the `banned` var (comma-separated) against the recipe's ingredients and
instructions, NOT the Critic report. The report is expected to name banned items
when flagging anachronisms.
"""

import json


def get_assert(output: str, context: dict) -> bool:  # noqa: ARG001
    banned = [
        s.strip().lower()
        for s in str((context.get("vars") or {}).get("banned", "")).split(",")
        if s.strip()
    ]
    if not banned:
        return False
    try:
        recipe = json.loads(output)["recipe"] or {}
    except TypeError, ValueError, KeyError:
        return False
    recipe_text = json.dumps(
        recipe.get("ingredients", []) + recipe.get("instructions", [])
    ).lower()
    return not any(b in recipe_text for b in banned)

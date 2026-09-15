"""Generic structural assertion: output parses as the pipeline result JSON.

Validates: iterations within the graph's max-3 cap, a final recipe exists, and
the Critic recorded a thematic_consistency verdict.
"""

import json

MAX_ITERATIONS = 3


def get_assert(output: str, context: dict) -> bool:  # noqa: ARG001
    try:
        result = json.loads(output)
    except TypeError, ValueError:
        return False
    recipe = result.get("recipe")
    report = result.get("report") or {}
    iterations = result.get("iterations", 0)
    if not recipe:
        return False
    if iterations < 1 or iterations > MAX_ITERATIONS:
        return False
    return report.get("thematic_consistency") is not None

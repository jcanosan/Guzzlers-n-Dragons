"""Critic agent: validates recipes for lore, science, and cookability."""

import structlog

from src.schemas.agents import AgentState
from src.schemas.response import (
    NutritionEstimate,
    PlausibilityReport,
    ValidationIssue,
    ValidationSeverity,
)
from src.tools.nutrition import lookup_nutrition

logger = structlog.get_logger()

THEMATIC_CONSTRAINTS = {
    "high_fantasy": {
        "forbidden": [
            "tomato",
            "potato",
            "corn",
            "chocolate",
            "chili pepper",
            "chili",
            "microwave",
            "blender",
        ],
        "tech_level": "pre_industrial",
        "allowed_magic": "ingredient_based",
    },
    "sci_fi": {
        "forbidden": [],
        "tech_level": "advanced",
        "allowed_magic": "technological",
    },
    "mythological": {
        "forbidden": [],
        "tech_level": "ancient",
        "allowed_magic": "divine",
    },
}


def _check_thematic(
    thematic_group: str, draft_ingredients: list[dict]
) -> tuple[list[ValidationIssue], str]:
    """Validate that no anachronistic ingredients appear in the recipe.

    Returns (issues, thematic_status) where thematic_status is
    "PASS" if no issues, "FAIL" if forbidden ingredients found.
    """
    issues: list[ValidationIssue] = []
    constraints = THEMATIC_CONSTRAINTS.get(thematic_group)
    if not constraints:
        return issues, "PASS"

    for word in constraints["forbidden"]:
        for ingredient_item in draft_ingredients:
            item_name = ingredient_item.get("item", "").lower()
            if word in item_name:
                issues.append(
                    ValidationIssue(
                        type="anachronism",
                        severity=ValidationSeverity.HIGH,
                        message=f"Forbidden ingredient '{word}'",
                        suggestion="Use theme-appropriate alternative",
                    )
                )
                return issues, "FAIL"

    return issues, "PASS"


def _check_cookability(
    draft, max_prep: int, max_cook: int
) -> list[ValidationIssue]:
    """Validate that the recipe is cookable within constraints.

    Checks for missing instructions and time limit violations.
    """
    issues: list[ValidationIssue] = []

    if not draft.instructions:
        issues.append(
            ValidationIssue(
                type="cookability",
                severity=ValidationSeverity.HIGH,
                message="Recipe has no instructions",
                suggestion="Add step-by-step cooking instructions",
            )
        )

    if draft.prep_time_minutes > max_prep:
        issues.append(
            ValidationIssue(
                type="cookability",
                severity=ValidationSeverity.MEDIUM,
                message=f"Prep time ({draft.prep_time_minutes}min)"
                f" exceeds max ({max_prep}min)",
                suggestion="Simplify preparation steps",
            )
        )

    if draft.cook_time_minutes > max_cook:
        issues.append(
            ValidationIssue(
                type="cookability",
                severity=ValidationSeverity.MEDIUM,
                message=f"Cook time ({draft.cook_time_minutes}min)"
                f" exceeds max ({max_cook}min)",
                suggestion="Reduce cooking time",
            )
        )

    return issues


async def _check_nutrition(ingredient_name: str) -> NutritionEstimate:
    """Look up nutrition data via the fallback chain (USDA → Fineli → OFF)."""
    nut_query = ingredient_name.lower().replace(" ", "_")
    nut_result = await lookup_nutrition(nut_query)

    if nut_result and nut_result.get("source") != "unavailable":
        return NutritionEstimate(
            calories_per_serving=nut_result.get("calories_per_serving"),
            protein_g=nut_result.get("protein_g"),
            carbs_g=nut_result.get("carbs_g"),
            fat_g=nut_result.get("fat_g"),
            notes=f"Source: {nut_result.get('source', 'unknown')}",
        )

    return NutritionEstimate(notes="No real ingredients found for analysis")


def _determine_verdict(thematic: str, issues: list) -> str:
    """Determine the final thematic_consistency verdict.

    - FAIL if any critical thematic/cookability issue was found
    - WARN if only advisory issues were found
    - PASS otherwise
    """
    if thematic == "FAIL":
        return "FAIL"
    if issues:
        return "WARN"
    return "PASS"


def _fail(reason: str) -> dict:
    """Return a FAIL result when no draft exists."""
    report = PlausibilityReport(
        thematic_consistency="FAIL",
        notes=[reason],
        validation_issues=[
            ValidationIssue(
                type="critical",
                severity=ValidationSeverity.HIGH,
                message=reason,
            )
        ],
    )
    return {"report": report.model_dump()}


async def run_critic(state: AgentState) -> dict:
    """Execute the Critic agent node.

    Validates thematic consistency, cookability, nutrition sanity,
    and returns a PlausibilityReport.
    """
    draft = state.draft_recipe
    if not draft:
        logger.warning("critic_skipped", reason="no_draft_recipe")
        return _fail("No draft recipe to validate")

    thematic_issues, thematic = _check_thematic(
        state.request.thematic_group, draft.ingredients
    )
    cook_issues = _check_cookability(
        draft,
        state.request.constraints.max_prep_time_minutes,
        state.request.constraints.max_cook_time_minutes,
    )

    nutrition = await _check_nutrition(state.request.fictional_ingredient)

    all_issues = thematic_issues + cook_issues
    verdict = _determine_verdict(thematic, all_issues)

    report = PlausibilityReport(
        thematic_consistency=verdict,
        notes=draft.plausibility_notes,
        nutrition_estimate=nutrition,
        validation_issues=all_issues,
    )

    logger.info(
        "critic_completed",
        result=verdict,
        issue_count=len(all_issues),
    )

    return {"report": report.model_dump()}

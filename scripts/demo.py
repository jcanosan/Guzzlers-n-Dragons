#!/usr/bin/env python3
"""Run one full Planner -> Creator -> Critic pass and print a readable trace.

Usage:
    PYTHONPATH=. uv run python scripts/demo.py \
        --ingredient "spice melange" --theme sci_fi
"""

import argparse
import asyncio
import json

from src.agents.graph import agent_graph
from src.schemas.agents import AgentState
from src.schemas.request import AlchemyRequest, Constraints
from src.services.database import init_db
from src.services.vector_store import vector_store


def _fmt(value: object) -> str:
    """Serialize a value for terminal display."""
    dump = getattr(value, "model_dump", None)
    if callable(dump):
        value = dump()
    if isinstance(value, (dict, list)):
        return json.dumps(value, default=str, indent=2)
    return str(value)


def _print_node(node: str, update: dict) -> None:
    if node == "planner":
        plan = update.get("planner_result")
        print(f"[planner] iteration {update.get('iteration', 1)}")
        if plan:
            print(f"  techniques: {', '.join(plan.technique_requirements)}")
            print(f"  flavor:     {_fmt(plan.flavor_profile)}")
            print(f"  textures:   {', '.join(plan.texture_goals)}")
            if plan.constraint_summary:
                print(f"  summary:    {plan.constraint_summary}")
            if plan.knowledge_queries:
                print(f"  queries:    {', '.join(plan.knowledge_queries)}")
    elif node == "creator":
        draft = update.get("draft_recipe")
        print("[creator]")
        if draft:
            print(f"  recipe:      {draft.name}")
            print(
                f"  servings:    {draft.servings} |"
                f" prep {draft.prep_time_minutes} min |"
                f" cook {draft.cook_time_minutes} min |"
                f" difficulty {draft.difficulty}"
            )
            print(f"  ingredients: {len(draft.ingredients)}")
    elif node == "critic":
        report = update.get("report") or {}
        print("[critic]")
        print(f"  verdict: {report.get('thematic_consistency')}")
        for issue in report.get("validation_issues") or []:
            print(
                f"  - {issue.get('severity')}: {issue.get('message')}"
                f" {issue.get('suggestion', '')}"
            )
        for note in (report.get("notes") or [])[:3]:
            print(f"  note: {note}")
    print()


def _print_result(state: dict) -> None:
    print("=== RESULT ===")
    draft = state.get("draft_recipe")
    report = state.get("report") or {}
    if draft:
        print(f"name:        {draft.name}")
        print(f"description: {draft.description}")
        print(
            "servings:    "
            f"{draft.servings} | prep {draft.prep_time_minutes} min"
            f" | cook {draft.cook_time_minutes} min | {draft.difficulty}"
        )
        print("ingredients:")
        for item in draft.ingredients:
            print(
                f"  - {item.get('amount', '')} {item.get('item', '')}"
                f" {f'({item.get("notes")})' if item.get('notes') else ''}"
            )
        print("instructions:")
        for i, step in enumerate(draft.instructions, 1):
            print(f"  {i}. {step}")
        if draft.plausibility_notes:
            print("creator notes:")
            for note in draft.plausibility_notes:
                print(f"  - {note}")
    if report:
        print("plausibility report:")
        print(f"  thematic_consistency: {report.get('thematic_consistency')}")
        nutrition = report.get("nutrition_estimate")
        if nutrition:
            print(f"  nutrition: {_fmt(nutrition)}")
        issues = report.get("validation_issues") or []
        if issues:
            print("  issues:")
            for issue in issues:
                print(f"    - {issue.get('severity')}: {issue.get('message')}")
    print(f"iterations: {state.get('iteration', 0)}")


async def run_demo(request: AlchemyRequest) -> None:
    initial = AgentState(request=request)
    print("=== Guzzlers-n-Dragons demo run ===")
    print(f"ingredient: {request.fictional_ingredient}")
    print(f"theme:      {request.thematic_group}")
    print(f"meal type:  {request.meal_type}")
    print()

    state: dict = {}
    async for chunk in agent_graph.astream(initial, stream_mode="updates"):
        for node, update in chunk.items():
            state.update(update)
            _print_node(node, update)

    _print_result(state)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run one full pass of the Planner -> Creator -> Critic pipeline"
        )
    )
    parser.add_argument(
        "--ingredient", default="spice melange", help="fictional ingredient"
    )
    parser.add_argument(
        "--theme",
        default="sci_fi",
        choices=["fantasy", "sci_fi", "mythological"],
        help="thematic group",
    )
    parser.add_argument("--meal-type", default="main course", help="meal type")
    parser.add_argument("--servings", type=int, default=4)
    parser.add_argument(
        "--dietary", nargs="*", default=[], help="dietary constraints"
    )
    parser.add_argument(
        "--difficulty",
        choices=["easy", "medium", "hard"],
        default=None,
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    init_db()
    vector_store.init()
    request = AlchemyRequest(
        fictional_ingredient=args.ingredient,
        meal_type=args.meal_type,
        thematic_group=args.theme,
        constraints=Constraints(
            servings=args.servings,
            dietary=args.dietary,
            difficulty=args.difficulty,
        ),
    )
    await run_demo(request)


if __name__ == "__main__":
    asyncio.run(main())

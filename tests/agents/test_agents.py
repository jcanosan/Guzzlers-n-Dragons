"""Tests for the Planner → Creator → Critic agent pipeline."""

from unittest.mock import AsyncMock, patch

import pytest
from langchain_core.messages import AIMessage

from src.agents.creator import run_creator
from src.agents.critic import run_critic
from src.agents.planner import run_planner
from src.schemas.agents import AgentState, DraftRecipe, PlannerResult
from src.schemas.request import AlchemyRequest, Constraints


@pytest.fixture
def basic_request() -> AlchemyRequest:
    return AlchemyRequest(
        fictional_ingredient="lembas",
        meal_type="bread",
        thematic_group="high_fantasy",
        constraints=Constraints(servings=4, max_prep_time_minutes=30),
    )


@pytest.fixture
def planner_result() -> PlannerResult:
    return PlannerResult(
        technique_requirements=["bake", "knead"],
        flavor_profile={"sweet": 0.6, "nutty": 0.3},
        texture_goals=["crisp exterior", "tender crumb"],
        constraint_summary="Quick bread under 30 min prep",
        knowledge_queries=["bread leavening", "honey sweetening"],
    )


@pytest.fixture
def draft_recipe() -> DraftRecipe:
    return DraftRecipe(
        name="Elven Lembas Bread",
        description="Light, sustaining waybread",
        ingredients=[{"item": "flour", "amount": "2 cups", "notes": ""}],
        instructions=["Mix ingredients", "Bake at 350F for 20 min"],
        prep_time_minutes=10,
        cook_time_minutes=20,
        servings=4,
        difficulty="easy",
        plausibility_notes=["Used honey as sweetener"],
    )


class TestPlanner:
    async def test_planner_with_mocked_llm(self, basic_request):
        state = AgentState(request=basic_request)

        mock_msg = AIMessage(
            content=(
                '{"technique_requirements": ["bake", "knead"],'
                ' "flavor_profile": {"sweet": 0.6},'
                ' "texture_goals": ["crisp"],'
                ' "constraint_summary": "Quick bread",'
                ' "knowledge_queries": ["bread leavening"]}'
            )
        )

        with patch(
            "src.agents.planner.call_llm",
            AsyncMock(return_value=mock_msg),
        ):
            result = await run_planner(state)
            assert isinstance(result["planner_result"], PlannerResult)
            assert result["planner_result"].knowledge_queries


class TestCreator:
    async def test_creator_with_mocked_llm(self, basic_request, planner_result):
        state = AgentState(request=basic_request, planner_result=planner_result)

        mock_msg = AIMessage(
            content=(
                '{"name": "Lembas Bread",'
                ' "description": "Elven waybread",'
                ' "ingredients": [{"item": "flour", "amount": "2 cups",'
                ' "notes": ""}],'
                ' "instructions": ["Mix", "Bake"],'
                ' "prep_time_minutes": 10,'
                ' "cook_time_minutes": 20,'
                ' "servings": 4,'
                ' "difficulty": "easy",'
                ' "plausibility_notes": ["Used honey"]}'
            )
        )

        with (
            patch(
                "src.agents.creator.call_llm",
                AsyncMock(return_value=mock_msg),
            ),
            patch(
                "src.tools.agent_tools.find_recipe_patterns",
                AsyncMock(return_value=[]),
            ),
        ):
            result = await run_creator(state)
            assert isinstance(result["draft_recipe"], DraftRecipe)
            assert result["draft_recipe"].name == "Lembas Bread"


class TestCritic:
    async def test_critic_passes_valid_recipe(
        self, basic_request, draft_recipe
    ):
        state = AgentState(request=basic_request, draft_recipe=draft_recipe)

        with patch(
            "src.agents.critic.lookup_nutrition",
            AsyncMock(
                return_value={
                    "calories_per_serving": 200,
                    "source": "usda",
                }
            ),
        ):
            result = await run_critic(state)
            report = result["report"]
            assert report["thematic_consistency"] == "PASS"
            assert len(report["validation_issues"]) == 0

    async def test_critic_fails_anachronism(self, basic_request):
        anachronistic = DraftRecipe(
            name="Bad Recipe",
            description="",
            ingredients=[{"item": "tomato", "amount": "1", "notes": ""}],
            instructions=["Mix"],
            prep_time_minutes=5,
            cook_time_minutes=10,
            servings=2,
            difficulty="easy",
        )
        state = AgentState(request=basic_request, draft_recipe=anachronistic)

        with patch(
            "src.agents.critic.lookup_nutrition",
            AsyncMock(return_value={"source": "unavailable"}),
        ):
            result = await run_critic(state)
            report = result["report"]
            assert report["thematic_consistency"] == "FAIL"
            assert report["validation_issues"][0]["type"] == "anachronism"

    async def test_critic_warns_time_exceeded(
        self, basic_request, draft_recipe
    ):
        draft_recipe.prep_time_minutes = 999
        state = AgentState(request=basic_request, draft_recipe=draft_recipe)

        with patch(
            "src.agents.critic.lookup_nutrition",
            AsyncMock(return_value={"source": "unavailable"}),
        ):
            result = await run_critic(state)
            report = result["report"]
            assert report["thematic_consistency"] == "WARN"
            assert any(
                i["type"] == "cookability" for i in report["validation_issues"]
            )


class TestGetPatternByMealType:
    def test_returns_none_for_unknown_type(self):
        from src.services.database import get_pattern_by_meal_type

        result = get_pattern_by_meal_type("nonexistent")
        assert result is None

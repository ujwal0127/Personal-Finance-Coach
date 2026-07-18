from app.agents.goal_agent import GoalAgent
from app.models.schemas import UserFinancialInput


def make_input(**overrides):
    base = dict(
        name="Test User", age=25, monthly_salary=50000,
        goal_name="Vacation", goal_target_amount=60000,
        goal_current_amount=20000, goal_target_months=8,
    )
    base.update(overrides)
    return UserFinancialInput(**base)


def test_goal_returns_none_when_not_specified():
    agent = GoalAgent()
    data = make_input(goal_name=None, goal_target_amount=None)
    result = agent.run(data, monthly_investable=5000)
    assert result is None


def test_goal_completion_percentage():
    agent = GoalAgent()
    data = make_input()
    result = agent.run(data, monthly_investable=5000)
    assert result.completion_percentage == round((20000 / 60000) * 100, 2)
    assert result.remaining_amount == 40000


def test_monthly_savings_needed_uses_target_months():
    agent = GoalAgent()
    data = make_input()
    result = agent.run(data, monthly_investable=5000)
    assert result.monthly_savings_needed == round(40000 / 8, 2)

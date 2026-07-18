import pytest
from app.agents.supervisor_agent import SupervisorAgent
from app.models.schemas import UserFinancialInput
from app.utils.validators import ValidationError


def make_input(**overrides):
    base = dict(
        name="Test User", age=28,
        monthly_salary=70000, freelance_income=0,
        expense_food=6000, expense_rent=18000, expense_shopping=3000,
        expense_entertainment=1500, expense_transportation=2000,
        expense_utilities=1500, expense_healthcare=1000,
        expense_education=0, expense_emi=0, expense_miscellaneous=1000,
        current_savings=50000, risk_tolerance="moderate",
        investment_experience="intermediate",
        goal_name="House Down Payment", goal_target_amount=500000,
        goal_current_amount=50000, goal_target_months=24,
    )
    base.update(overrides)
    return UserFinancialInput(**base)


def test_full_report_generation():
    supervisor = SupervisorAgent()
    data = make_input()
    report = supervisor.run(data)

    assert report.user_name == "Test User"
    assert report.income.total_monthly_income > 0
    assert report.expenses.total_monthly_expenses > 0
    assert 0 <= report.financial_health_score <= 100
    assert report.goal is not None
    assert report.goal.goal_name == "House Down Payment"
    assert len(report.action_plan) > 0


def test_report_without_goal():
    supervisor = SupervisorAgent()
    data = make_input(goal_name=None, goal_target_amount=None)
    report = supervisor.run(data)
    assert report.goal is None


def test_zero_income_raises_validation_error():
    supervisor = SupervisorAgent()
    data = make_input(monthly_salary=0, freelance_income=0, rental_income=0, passive_income=0)
    with pytest.raises(ValidationError):
        supervisor.run(data)

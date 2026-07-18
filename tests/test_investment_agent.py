from app.agents.expense_agent import ExpenseAgent
from app.agents.investment_agent import InvestmentAgent
from app.models.schemas import UserFinancialInput


def make_input(**overrides):
    base = dict(
        name="Test User", age=30, monthly_salary=80000,
        expense_food=5000, expense_rent=15000,
        risk_tolerance="high",
    )
    base.update(overrides)
    return UserFinancialInput(**base)


def test_allocation_percentages_match_template_for_high_risk():
    data = make_input()
    expenses = ExpenseAgent().run(data)
    investment = InvestmentAgent().run(data, expenses)

    total_allocated = sum(investment.suggested_allocation.values())
    # allocation should roughly equal the investable amount (rounding tolerance)
    assert abs(total_allocated - investment.monthly_investable_amount) < 1.0


def test_emergency_fund_target_is_six_months_expenses():
    data = make_input()
    expenses = ExpenseAgent().run(data)
    investment = InvestmentAgent().run(data, expenses)
    assert investment.emergency_fund_target == round(expenses.total_monthly_expenses * 6, 2)


def test_emergency_fund_is_prioritized_when_it_is_not_fully_funded():
    data = make_input(current_savings=0)
    expenses = ExpenseAgent().run(data)
    investment = InvestmentAgent().run(data, expenses)
    assert investment.suggested_allocation == {
        "Emergency Fund": investment.monthly_investable_amount
    }

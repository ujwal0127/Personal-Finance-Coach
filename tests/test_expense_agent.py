from app.agents.expense_agent import ExpenseAgent
from app.models.schemas import UserFinancialInput


def make_input(**overrides):
    base = dict(
        name="Test User", age=25,
        monthly_salary=50000,
        expense_food=5000, expense_rent=15000, expense_shopping=2000,
        expense_entertainment=1000, expense_transportation=1500,
        expense_utilities=1200, expense_healthcare=800,
        expense_education=0, expense_emi=0, expense_miscellaneous=500,
    )
    base.update(overrides)
    return UserFinancialInput(**base)


def test_total_expenses_sums_all_categories():
    agent = ExpenseAgent()
    data = make_input()
    result = agent.run(data)
    assert result.total_monthly_expenses == 5000 + 15000 + 2000 + 1000 + 1500 + 1200 + 800 + 0 + 0 + 500


def test_largest_category_is_rent():
    agent = ExpenseAgent()
    data = make_input()
    result = agent.run(data)
    assert result.largest_category == "rent"
    assert result.largest_category_amount == 15000


def test_savings_potential_never_negative():
    agent = ExpenseAgent()
    data = make_input(monthly_salary=1000, expense_rent=50000)
    result = agent.run(data)
    assert result.savings_potential == 0

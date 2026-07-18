from app.agents.income_agent import IncomeAgent
from app.models.schemas import UserFinancialInput


def make_input(**overrides):
    base = dict(
        name="Test User", age=25,
        monthly_salary=50000, freelance_income=5000,
        rental_income=0, passive_income=0, annual_bonus=12000,
    )
    base.update(overrides)
    return UserFinancialInput(**base)


def test_total_income_includes_bonus_amortized():
    agent = IncomeAgent()
    data = make_input()
    result = agent.run(data)
    expected = 50000 + 5000 + 12000 / 12
    assert result.total_monthly_income == round(expected, 2)


def test_stable_vs_variable_split():
    agent = IncomeAgent()
    data = make_input(rental_income=3000, passive_income=1000)
    result = agent.run(data)
    assert result.stable_income == 50000 + 3000
    assert result.variable_income == 5000 + 1000

import pytest
from pydantic import ValidationError as PydanticValidationError

from app.models.schemas import UserFinancialInput
from app.utils.validators import validate_user_input


def test_annual_bonus_counts_as_income():
    data = UserFinancialInput(name="Bonus User", age=25, annual_bonus=120000)
    validate_user_input(data)


def test_negative_financial_amounts_are_rejected():
    with pytest.raises(PydanticValidationError):
        UserFinancialInput(name="Test User", age=25, monthly_salary=-1)


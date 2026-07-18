"""Input validation helpers beyond what Pydantic enforces automatically."""

from app.models.schemas import UserFinancialInput


class ValidationError(Exception):
    pass


def validate_user_input(data: UserFinancialInput) -> None:
    """Raises ValidationError if the input data doesn't make financial sense."""

    total_monthly_income = (
        data.monthly_salary
        + data.freelance_income
        + data.rental_income
        + data.passive_income
        + (data.annual_bonus / 12)
    )
    if total_monthly_income <= 0:
        raise ValidationError("At least one income source must be greater than zero.")

    if data.risk_tolerance not in ("low", "moderate", "high"):
        raise ValidationError("risk_tolerance must be 'low', 'moderate', or 'high'.")

    if data.investment_experience not in ("beginner", "intermediate", "expert"):
        raise ValidationError(
            "investment_experience must be 'beginner', 'intermediate', or 'expert'."
        )

    if data.goal_target_amount is not None and data.goal_target_amount < 0:
        raise ValidationError("goal_target_amount cannot be negative.")

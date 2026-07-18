"""
Pure financial math helpers used by multiple agents.
Kept dependency-free so they're trivial to unit test.
"""

from __future__ import annotations


def total_income(salary: float, freelance: float, rental: float,
                  passive: float, annual_bonus: float) -> float:
    """Total monthly income, spreading the annual bonus across 12 months."""
    return salary + freelance + rental + passive + (annual_bonus / 12)


def stable_vs_variable(salary: float, rental: float,
                        freelance: float, passive: float) -> tuple[float, float]:
    """Salary + rental are treated as stable; freelance + passive as variable."""
    stable = salary + rental
    variable = freelance + passive
    return stable, variable


def savings_potential(income: float, expenses: float) -> float:
    return max(income - expenses, 0)


def emergency_fund_target(monthly_expenses: float, months: int = 6) -> float:
    return monthly_expenses * months


def goal_completion_percentage(current: float, target: float) -> float:
    if target <= 0:
        return 0.0
    return min(round((current / target) * 100, 2), 100.0)


def months_to_goal(remaining_amount: float, monthly_contribution: float) -> float | None:
    if monthly_contribution <= 0:
        return None
    return round(remaining_amount / monthly_contribution, 1)


def monthly_savings_needed(remaining_amount: float, months_remaining: int | None) -> float | None:
    if not months_remaining or months_remaining <= 0:
        return None
    return round(remaining_amount / months_remaining, 2)


def financial_health_score(income: float, expenses: float, savings_rate: float,
                            has_emergency_fund: bool) -> int:
    """
    Simple 0-100 heuristic score:
      - savings rate contributes up to 60 points
      - expense-to-income ratio contributes up to 25 points
      - having an emergency fund contributes 15 points
    """
    score = 0

    # Savings rate component (0-60)
    score += min(savings_rate * 100, 60)

    # Expense ratio component (0-25): lower expense/income ratio is better
    if income > 0:
        expense_ratio = expenses / income
        score += max(0, (1 - expense_ratio)) * 25
    score = min(score, 85)

    # Emergency fund bonus
    if has_emergency_fund:
        score += 15

    return int(round(min(score, 100)))

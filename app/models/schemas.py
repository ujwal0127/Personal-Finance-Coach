"""
Pydantic schemas shared across all agents.

These models define the inputs each agent expects and the outputs each
agent produces, so the Supervisor Agent can pass structured data between
them safely.
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# User Input
# ---------------------------------------------------------------------------

class UserFinancialInput(BaseModel):
    """Raw financial data collected from the user."""

    name: str
    age: int = Field(ge=16, le=100)

    # Income sources
    monthly_salary: float = Field(default=0, ge=0)
    freelance_income: float = Field(default=0, ge=0)
    rental_income: float = Field(default=0, ge=0)
    passive_income: float = Field(default=0, ge=0)
    annual_bonus: float = Field(default=0, ge=0)

    # Expenses (monthly, by category)
    expense_food: float = Field(default=0, ge=0)
    expense_rent: float = Field(default=0, ge=0)
    expense_shopping: float = Field(default=0, ge=0)
    expense_entertainment: float = Field(default=0, ge=0)
    expense_transportation: float = Field(default=0, ge=0)
    expense_utilities: float = Field(default=0, ge=0)
    expense_healthcare: float = Field(default=0, ge=0)
    expense_education: float = Field(default=0, ge=0)
    expense_emi: float = Field(default=0, ge=0)
    expense_miscellaneous: float = Field(default=0, ge=0)

    # Investment profile
    current_savings: float = Field(default=0, ge=0)
    risk_tolerance: str = Field(default="moderate")  # low / moderate / high
    investment_experience: str = Field(default="beginner")  # beginner/intermediate/expert

    # Goals
    goal_name: Optional[str] = None
    goal_target_amount: Optional[float] = Field(default=None, gt=0)
    goal_current_amount: Optional[float] = Field(default=0, ge=0)
    goal_target_months: Optional[int] = Field(default=None, gt=0)


# ---------------------------------------------------------------------------
# Agent Outputs
# ---------------------------------------------------------------------------

class IncomeAnalysis(BaseModel):
    total_monthly_income: float
    stable_income: float
    variable_income: float
    income_breakdown: dict
    summary: str


class ExpenseAnalysis(BaseModel):
    total_monthly_expenses: float
    expense_breakdown: dict
    largest_category: str
    largest_category_amount: float
    savings_potential: float
    summary: str


class InvestmentRecommendation(BaseModel):
    monthly_investable_amount: float
    emergency_fund_target: float
    suggested_allocation: dict  # e.g. {"SIP": 40, "FD": 20, "Gold": 10, "Emergency Fund": 30}
    risk_analysis: str
    summary: str


class GoalStatus(BaseModel):
    goal_name: str
    target_amount: float
    current_amount: float
    remaining_amount: float
    completion_percentage: float
    monthly_savings_needed: Optional[float]
    estimated_months_to_complete: Optional[float]
    summary: str


class FinancialReport(BaseModel):
    user_name: str
    income: IncomeAnalysis
    expenses: ExpenseAnalysis
    investment: InvestmentRecommendation
    goal: Optional[GoalStatus] = None
    net_monthly_savings: float
    financial_health_score: int  # 0-100
    action_plan: list[str]
    overall_summary: str

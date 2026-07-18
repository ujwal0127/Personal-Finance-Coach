"""
Shared state object passed between nodes in the LangGraph workflow.

LangGraph nodes typically operate on a TypedDict/dict-like state. Each node
reads what it needs from the state and writes its result back in.
"""

from __future__ import annotations
from typing import TypedDict, Optional
from app.models.schemas import (
    UserFinancialInput, IncomeAnalysis, ExpenseAnalysis,
    InvestmentRecommendation, GoalStatus, FinancialReport,
)


class GraphState(TypedDict, total=False):
    user_input: UserFinancialInput
    income: IncomeAnalysis
    expenses: ExpenseAnalysis
    investment: InvestmentRecommendation
    goal: Optional[GoalStatus]
    report: FinancialReport
    error: Optional[str]

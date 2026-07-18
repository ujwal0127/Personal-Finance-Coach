"""Streamlit component for rendering ExpenseAnalysis."""

import streamlit as st
from app.models.schemas import ExpenseAnalysis


def render(expenses: ExpenseAnalysis) -> None:
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Monthly Expenses", f"{expenses.total_monthly_expenses:,.2f}")
    c2.metric("Largest Category", expenses.largest_category.title())
    c3.metric("Savings Potential", f"{expenses.savings_potential:,.2f}")

    st.bar_chart(expenses.expense_breakdown)
    st.write(expenses.summary)

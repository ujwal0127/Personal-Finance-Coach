"""Streamlit component for rendering IncomeAnalysis."""

import streamlit as st
from app.models.schemas import IncomeAnalysis


def render(income: IncomeAnalysis) -> None:
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Monthly Income", f"{income.total_monthly_income:,.2f}")
    c2.metric("Stable Income", f"{income.stable_income:,.2f}")
    c3.metric("Variable Income", f"{income.variable_income:,.2f}")

    st.bar_chart(income.income_breakdown)
    st.write(income.summary)

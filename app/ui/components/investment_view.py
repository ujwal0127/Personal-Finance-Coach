"""Streamlit component for rendering InvestmentRecommendation."""

import streamlit as st
from app.models.schemas import InvestmentRecommendation


def render(investment: InvestmentRecommendation) -> None:
    c1, c2 = st.columns(2)
    c1.metric("Monthly Investable Amount", f"{investment.monthly_investable_amount:,.2f}")
    c2.metric("Emergency Fund Target", f"{investment.emergency_fund_target:,.2f}")

    st.bar_chart(investment.suggested_allocation)
    st.caption(f"Risk analysis: {investment.risk_analysis}")
    st.write(investment.summary)

"""Streamlit component for rendering GoalStatus."""

import streamlit as st
from typing import Optional
from app.models.schemas import GoalStatus


def render(goal: Optional[GoalStatus]) -> None:
    if goal is None:
        st.info("No goal was specified for this report.")
        return

    st.subheader(goal.goal_name)
    st.progress(min(goal.completion_percentage / 100, 1.0))
    st.caption(f"{goal.completion_percentage:.1f}% complete "
               f"({goal.current_amount:,.2f} / {goal.target_amount:,.2f})")

    c1, c2 = st.columns(2)
    c1.metric("Remaining Amount", f"{goal.remaining_amount:,.2f}")
    if goal.monthly_savings_needed:
        c2.metric("Monthly Savings Needed", f"{goal.monthly_savings_needed:,.2f}")
    elif goal.estimated_months_to_complete:
        c2.metric("Estimated Months to Complete", f"{goal.estimated_months_to_complete}")

    st.write(goal.summary)

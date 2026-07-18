"""Goals page — progress toward the user's financial goal."""

import streamlit as st

from app.ui.common import inject_css, money, init_session_state, render_side_panel
from app.ui.components import goal_view


def render():
    init_session_state()
    inject_css()

    st.title("🎯 Goals")
    st.caption("Track your progress toward what you're saving for.")

    if st.session_state.report is None:
        st.info(
            "No report yet. Use the **Dashboard** page in the sidebar to fill in "
            "your details and generate your first financial report."
        )
        return

    report = st.session_state.report

    main_col, side_col = st.columns([3, 1])

    with main_col:
        goal_view.render(report.goal)

        if report.goal:
            g = report.goal
            pct = min(g.completion_percentage, 100)
            st.markdown('<div class="fc-section-title">Progress</div>', unsafe_allow_html=True)
            st.markdown(
                f"""<div style="margin-bottom:6px;font-weight:600;color:#e5e7eb;">{g.goal_name}</div>
                <div class="fc-bar-track"><div class="fc-bar-fill" style="width:{pct}%;background:#22c55e;"></div></div>
                <div style="font-size:0.85rem;color:#9aa0ab;margin-top:6px;">
                    {money(g.current_amount)} / {money(g.target_amount)} ({pct:.0f}% complete, {money(g.remaining_amount)} remaining)
                </div>""",
                unsafe_allow_html=True,
            )
            if g.monthly_savings_needed:
                st.caption(f"Needs ~{money(g.monthly_savings_needed)}/month to hit your target date.")
            elif g.estimated_months_to_complete:
                st.caption(f"Estimated {g.estimated_months_to_complete:.0f} months to complete at current pace.")
            st.markdown('<div class="fc-section-title">🎯 Goal Insight</div>', unsafe_allow_html=True)
            st.write(g.summary)
            goal_summary = g.summary
        else:
            st.info("No goal set for this report. Add one in the form on the **Dashboard** page.")
            goal_summary = "No goal set yet."

    with side_col:
        render_side_panel(report, goal_summary, key_prefix="goals")

"""Income page — deep dive into income sources and trend."""

import streamlit as st
import plotly.graph_objects as go

from app.ui.common import PALETTE, inject_css, money, init_session_state, render_side_panel
from app.ui.components import income_view


def render():
    init_session_state()
    inject_css()

    st.title("💵 Income")
    st.caption("A breakdown of where your money comes from.")

    if st.session_state.report is None:
        st.info(
            "No report yet. Use the **Dashboard** page in the sidebar to fill in "
            "your details and generate your first financial report."
        )
        return

    report = st.session_state.report
    history = st.session_state.history

    main_col, side_col = st.columns([3, 1])

    with main_col:
        income_view.render(report.income)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="fc-section-title">Income Sources</div>', unsafe_allow_html=True)
            breakdown = report.income.income_breakdown
            labels = [k.replace("_", " ").title() for k, v in breakdown.items() if v > 0]
            values = [v for v in breakdown.values() if v > 0]
            if values:
                fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.55,
                                        marker=dict(colors=PALETTE), textinfo="percent"))
                fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10),
                                   paper_bgcolor="rgba(0,0,0,0)", font_color="#e5e7eb")
                st.plotly_chart(fig, width="stretch")
            else:
                st.caption("No income recorded.")

        with c2:
            st.markdown('<div class="fc-section-title">Income Trend</div>', unsafe_allow_html=True)
            if history:
                dates = [h["date"].strftime("%b %d") for h in history]
                fig = go.Figure(go.Scatter(
                    x=dates, y=[h["income"] for h in history], fill="tozeroy",
                    line=dict(color="#22c55e", width=3), fillcolor="rgba(34,197,94,0.25)",
                ))
                fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10),
                                   paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                   font_color="#e5e7eb")
                st.plotly_chart(fig, width="stretch")
            else:
                st.caption("No history yet — generate more reports to see a trend.")
        st.markdown('<div class="fc-section-title">💰 Income Insight</div>', unsafe_allow_html=True)
        st.write(report.income.summary)
        st.caption(f"Stable: {money(report.income.stable_income)} · Variable: {money(report.income.variable_income)}")

    with side_col:
        goal_summary = report.goal.summary if report.goal else "Set a goal on the Dashboard page to get tailored tracking."
        render_side_panel(report, goal_summary, key_prefix="income")

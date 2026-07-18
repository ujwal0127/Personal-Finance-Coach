"""Investment page — allocation strategy and recommendations."""

import streamlit as st

from app.ui.common import PALETTE, inject_css, money, init_session_state, render_side_panel
from app.ui.components import investment_view


def render():
    init_session_state()
    inject_css()

    st.title("📈 Investment")
    st.caption("Where your surplus could be put to work.")

    if st.session_state.report is None:
        st.info(
            "No report yet. Use the **Dashboard** page in the sidebar to fill in "
            "your details and generate your first financial report."
        )
        return

    report = st.session_state.report

    main_col, side_col = st.columns([3, 1])

    with main_col:
        investment_view.render(report.investment)
        st.markdown('<div class="fc-section-title">Suggested Allocation</div>', unsafe_allow_html=True)
        allocation = report.investment.suggested_allocation
        total_alloc = sum(allocation.values()) or 1
        cols = st.columns(len(allocation) or 1)
        for i, (label, amount) in enumerate(allocation.items()):
            pct = amount / total_alloc * 100
            color = PALETTE[i % len(PALETTE)]
            with cols[i]:
                st.markdown(
                    f"""<div class="fc-alloc-card" style="background:{color};">
                        <div style="font-weight:600;">{label}</div>
                        <div style="font-size:1.2rem;font-weight:700;">{pct:.0f}%</div>
                        <div style="font-size:0.8rem;opacity:0.9;">{money(amount)}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
        st.markdown('<div class="fc-section-title">📈 Investment Insight</div>', unsafe_allow_html=True)
        st.write(report.investment.summary)
        st.caption(f"Risk approach: {report.investment.risk_analysis}")
        st.caption(
            f"Monthly investable amount: {money(report.investment.monthly_investable_amount)} · "
            f"Emergency fund target: {money(report.investment.emergency_fund_target)}"
        )

    with side_col:
        goal_summary = report.goal.summary if report.goal else "Set a goal on the Dashboard page to get tailored tracking."
        render_side_panel(report, goal_summary, key_prefix="investment")

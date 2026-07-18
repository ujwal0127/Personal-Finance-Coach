"""Expenses page — deep dive into spending categories and budget utilization."""

import streamlit as st
import plotly.graph_objects as go

from app.ui.common import PALETTE, inject_css, money, init_session_state, render_side_panel
from app.ui.components import expense_view


def render():
    init_session_state()
    inject_css()

    st.title("💳 Expenses")
    st.caption("Where your money is going, and how it compares to your income.")

    if st.session_state.report is None:
        st.info(
            "No report yet. Use the **Dashboard** page in the sidebar to fill in "
            "your details and generate your first financial report."
        )
        return

    report = st.session_state.report
    history = st.session_state.history
    breakdown = report.expenses.expense_breakdown
    income_total = max(report.income.total_monthly_income, 1)

    main_col, side_col = st.columns([3, 1])

    with main_col:
        expense_view.render(report.expenses)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="fc-section-title">Expense Breakdown</div>', unsafe_allow_html=True)
            labels = [k.title() for k, v in breakdown.items() if v > 0]
            values = [v for v in breakdown.values() if v > 0]
            if values:
                fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.6,
                                        marker=dict(colors=PALETTE), textinfo="none"))
                fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10),
                                   paper_bgcolor="rgba(0,0,0,0)", font_color="#e5e7eb",
                                   annotations=[dict(text=f"{money(report.expenses.total_monthly_expenses)}<br>Total",
                                                      showarrow=False, font=dict(size=14, color="#f2f3f5"))])
                st.plotly_chart(fig, width="stretch")
            else:
                st.caption("No expenses recorded.")

        with c2:
            st.markdown('<div class="fc-section-title">Expense Trend</div>', unsafe_allow_html=True)
            if history:
                dates = [h["date"].strftime("%b %d") for h in history]
                fig = go.Figure(go.Scatter(
                    x=dates, y=[h["expenses"] for h in history], fill="tozeroy",
                    line=dict(color="#ef4444", width=3), fillcolor="rgba(239,68,68,0.25)",
                ))
                fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10),
                                   paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                   font_color="#e5e7eb")
                st.plotly_chart(fig, width="stretch")
            else:
                st.caption("No history yet — generate more reports to see a trend.")
        st.markdown('<div class="fc-section-title">Budget Utilization</div>', unsafe_allow_html=True)
        st.caption("Each category's share of your total monthly income.")
        top_categories = sorted(breakdown.items(), key=lambda kv: kv[1], reverse=True)
        for i, (cat, amt) in enumerate(top_categories):
            if amt <= 0:
                continue
            pct = min(amt / income_total * 100, 100)
            color = PALETTE[i % len(PALETTE)]
            st.markdown(
                f"""<div style="margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#e5e7eb;">
                        <span>{cat.title()}</span><span>{pct:.0f}% ({money(amt)})</span>
                    </div>
                    <div class="fc-bar-track"><div class="fc-bar-fill" style="width:{pct}%;background:{color};"></div></div>
                </div>""",
                unsafe_allow_html=True,
            )
        st.markdown('<div class="fc-section-title">⚠️ Expense Insight</div>', unsafe_allow_html=True)
        st.write(report.expenses.summary)
        st.caption(
            f"Largest category: {report.expenses.largest_category.title()} "
            f"({money(report.expenses.largest_category_amount)}) · "
            f"Savings potential: {money(report.expenses.savings_potential)}"
        )

    with side_col:
        goal_summary = report.goal.summary if report.goal else "Set a goal on the Dashboard page to get tailored tracking."
        render_side_panel(report, goal_summary, key_prefix="expenses")

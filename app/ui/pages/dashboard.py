"""Dashboard page — input form plus a high-level financial overview."""

import streamlit as st
import plotly.graph_objects as go
import time

from app.models.schemas import UserFinancialInput
from app.services.report_generator import generate_report
from app.services.financial_health import score_label, score_color
from app.utils.pdf_export import generate_pdf
from app.ui.common import (
    PALETTE, inject_css, money, pct_delta, metric_card,
    init_session_state, load_history, render_side_panel,
)


def render():
    init_session_state()
    inject_css()

    st.title("💰 Personal Finance Coach")
    st.caption("A Multi-Agent AI System for Smart Financial Planning")

    form_expanded = st.session_state.report is None
    with st.expander("✏️ Your Details", expanded=form_expanded):
        left_pad, main_col, right_pad = st.columns([1, 3, 1])
        with main_col:
            with st.form("financial_details_form"):
                st.header("Your Details")
                c1, c2 = st.columns(2)
                with c1:
                    name = st.text_input("Name", "Alex")
                with c2:
                    age = st.number_input("Age", min_value=16, max_value=100, value=27)

                st.subheader("Income")
                c1, c2 = st.columns(2)
                with c1:
                    salary = st.number_input("Monthly Salary", min_value=0.0, value=60000.0, step=1000.0)
                    rental = st.number_input("Rental Income", min_value=0.0, value=0.0, step=500.0)
                    bonus = st.number_input("Annual Bonus", min_value=0.0, value=0.0, step=1000.0)
                with c2:
                    freelance = st.number_input("Freelance Income", min_value=0.0, value=0.0, step=500.0)
                    passive = st.number_input("Passive Income", min_value=0.0, value=0.0, step=500.0)

                st.subheader("Monthly Expenses")
                c1, c2 = st.columns(2)
                with c1:
                    food = st.number_input("Food", min_value=0.0, value=8000.0, step=500.0)
                    shopping = st.number_input("Shopping", min_value=0.0, value=4000.0, step=500.0)
                    transportation = st.number_input("Transportation", min_value=0.0, value=3000.0, step=500.0)
                    healthcare = st.number_input("Healthcare", min_value=0.0, value=1500.0, step=500.0)
                    emi = st.number_input("EMI", min_value=0.0, value=0.0, step=500.0)
                with c2:
                    rent = st.number_input("Rent", min_value=0.0, value=15000.0, step=500.0)
                    entertainment = st.number_input("Entertainment", min_value=0.0, value=2000.0, step=500.0)
                    utilities = st.number_input("Utilities", min_value=0.0, value=2500.0, step=500.0)
                    education = st.number_input("Education", min_value=0.0, value=0.0, step=500.0)
                    misc = st.number_input("Miscellaneous", min_value=0.0, value=2000.0, step=500.0)

                st.subheader("Investment Profile")
                c1, c2, c3 = st.columns(3)
                with c1:
                    savings = st.number_input("Current Savings", min_value=0.0, value=30000.0, step=1000.0)
                with c2:
                    risk = st.selectbox("Risk Tolerance", ["low", "moderate", "high"], index=1)
                with c3:
                    experience = st.selectbox(
                        "Investment Experience", ["beginner", "intermediate", "expert"], index=0
                    )

                st.subheader("Goal (optional)")
                c1, c2 = st.columns(2)
                with c1:
                    goal_name = st.text_input("Goal Name", "Emergency Fund")
                    goal_target = st.number_input("Goal Target Amount", min_value=0.0, value=100000.0, step=5000.0)
                with c2:
                    goal_current = st.number_input("Goal Current Amount", min_value=0.0, value=20000.0, step=1000.0)
                    goal_months = st.number_input("Target Months to Complete", min_value=0, value=12, step=1)

                submitted = st.form_submit_button(
                    "Generate Financial Report", type="primary", width="stretch"
                )

    if submitted:
        user_input = UserFinancialInput(
            name=name,
            age=age,
            monthly_salary=salary,
            freelance_income=freelance,
            rental_income=rental,
            passive_income=passive,
            annual_bonus=bonus,
            expense_food=food,
            expense_rent=rent,
            expense_shopping=shopping,
            expense_entertainment=entertainment,
            expense_transportation=transportation,
            expense_utilities=utilities,
            expense_healthcare=healthcare,
            expense_education=education,
            expense_emi=emi,
            expense_miscellaneous=misc,
            current_savings=savings,
            risk_tolerance=risk,
            investment_experience=experience,
            goal_name=goal_name or None,
            goal_target_amount=goal_target if goal_target > 0 else None,
            goal_current_amount=goal_current,
            goal_target_months=goal_months if goal_months > 0 else None,
        )

        status = st.status(
            "🚀 Generating Your Financial Report...",
            expanded=True,
        )

        progress = st.progress(0)

        try:

            progress.progress(10)
            status.write("📋 Collecting your financial information...")
            time.sleep(0.15)

            progress.progress(25)
            status.write("💰 Income Agent analyzing salary and income...")
            time.sleep(0.15)

            progress.progress(45)
            status.write("💳 Expense Agent analyzing spending...")
            time.sleep(0.15)

            progress.progress(65)
            status.write("📈 Investment Agent preparing recommendations...")
            time.sleep(0.15)

            progress.progress(80)
            status.write("🎯 Goal Agent evaluating your financial goals...")
            time.sleep(0.15)

            progress.progress(90)
            status.write("🤖 Supervisor Agent combining all reports...")

            report = generate_report(
                user_input,
                persist=True,
            )

            progress.progress(100)
            time.sleep(0.4)
            progress.empty()

            status.update(
                label="✅ Financial Report Generated Successfully!",
                state="complete",
                expanded=False,
            )

        except Exception as e:

            status.update(
                label="❌ Report Generation Failed",
                state="error",
            )

            st.error(f"Could not generate report: {e}")
            st.stop()
        st.session_state.report = report
        st.session_state.history = load_history(name, age)
        st.session_state.chat_messages = []

        st.toast("🎉 Financial Report Ready!", icon="✅")

    report = st.session_state.report
    if report is None:
        st.info("Fill in your details above and click **Generate Financial Report**.")
        return

    history = st.session_state.history
    prev = history[-2] if len(history) >= 2 else None
    income_total = max(report.income.total_monthly_income, 1)
    breakdown = report.expenses.expense_breakdown
    goal_summary = report.goal.summary if report.goal else "Set a goal in the form above to get tailored tracking."


    dash_col, side_col = st.columns([3, 1])

    with dash_col:
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            metric_card("💰", "Monthly Income", money(report.income.total_monthly_income),
                        pct_delta(report.income.total_monthly_income, prev["income"]) if prev else None)
        with m2:
            metric_card("💳", "Total Expenses", money(report.expenses.total_monthly_expenses),
                        pct_delta(report.expenses.total_monthly_expenses, prev["expenses"]) if prev else None)
        with m3:
            metric_card("🏦", "Monthly Savings", money(report.net_monthly_savings),
                        pct_delta(report.net_monthly_savings, prev["savings"]) if prev else None)
        with m4:
            metric_card("🏆", "Financial Health Score", f"{report.financial_health_score}/100",
                        None, caption=f"{score_label(report.financial_health_score)}")

        c1, c2 = st.columns([1.4, 1])
        with c1:
            st.markdown('<div class="fc-section-title">Income vs Expenses Trend</div>', unsafe_allow_html=True)
            if history:
                dates = [h["date"].strftime("%b %d") for h in history]
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=dates, y=[h["income"] for h in history],
                                          name="Income", line=dict(color="#22c55e", width=3)))
                fig.add_trace(go.Scatter(x=dates, y=[h["expenses"] for h in history],
                                          name="Expenses", line=dict(color="#ef4444", width=3)))
                fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10),
                                   paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                   font_color="#e5e7eb", legend=dict(orientation="h", y=1.15))
                st.plotly_chart(fig, width="stretch")
                if len(history) < 3:
                    st.caption("Trend fills in as you generate more reports over time.")
            else:
                st.caption("No history yet — this trend will build up as you generate more reports.")

        with c2:
            st.markdown('<div class="fc-section-title">Expense Breakdown</div>', unsafe_allow_html=True)
            labels = [k.title() for k, v in breakdown.items() if v > 0]
            values = [v for v in breakdown.values() if v > 0]
            if values:
                fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.6,
                                        marker=dict(colors=PALETTE), textinfo="none"))
                fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10),
                                   paper_bgcolor="rgba(0,0,0,0)", font_color="#e5e7eb",
                                   showlegend=True, legend=dict(orientation="v", font=dict(size=11)),
                                   annotations=[dict(text=f"{money(report.expenses.total_monthly_expenses)}<br>Total",
                                                      showarrow=False, font=dict(size=14, color="#f2f3f5"))])
                st.plotly_chart(fig, width="stretch")
            else:
                st.caption("No expenses recorded.")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="fc-section-title">Financial Health Gauge</div>', unsafe_allow_html=True)
            score = report.financial_health_score
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=score,
                number={"font": {"size": 36, "color": "#f2f3f5"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#9aa0ab"},
                    "bar": {"color": score_color(score)},
                    "bgcolor": "rgba(0,0,0,0)",
                    "steps": [
                        {"range": [0, 30], "color": "#c62828"},
                        {"range": [30, 50], "color": "#f57c00"},
                        {"range": [50, 70], "color": "#fbc02d"},
                        {"range": [70, 85], "color": "#66bb6a"},
                        {"range": [85, 100], "color": "#2e7d32"},
                    ],
                },
            ))
            fig.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=10),
                               paper_bgcolor="rgba(0,0,0,0)", font_color="#e5e7eb")
            st.plotly_chart(fig, width="stretch")
            st.caption(f"{score_label(score)} — {report.overall_summary}")

        with c2:
            st.markdown('<div class="fc-section-title">AI Insights</div>', unsafe_allow_html=True)
            savings_pct = (report.net_monthly_savings / income_total * 100) if income_total else 0
            insights = [
                ("💰", "Income", report.income.summary, "#14351f"),
                ("⚠️", "Expenses", report.expenses.summary, "#3a2a12"),
                ("📈", "Savings", f"You're saving about {savings_pct:.0f}% of your income. "
                                  f"{'Keep it up!' if savings_pct >= 15 else 'Try to increase this over time.'}", "#122238"),
                ("🎯", "Goal", goal_summary, "#2a1338"),
            ]
            for icon, title, text, bg in insights:
                st.markdown(
                    f"""<div class="fc-insight-card" style="background:{bg};">
                        <div style="font-weight:600;margin-bottom:4px;">{icon} {title}</div>
                        <div style="font-size:0.82rem;color:#d1d5db;">{text}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

        st.divider()

        st.subheader("📋 Action Plan")
        for item in report.action_plan:
            st.markdown(f"- {item}")

        st.caption(
            "For a deeper dive, use the **Income**, **Expenses**, **Investment**, and "
            "**Goals** pages in the sidebar."
        )
        # -------------------------------------------------------
        # Export Financial Report
        # -------------------------------------------------------

        st.markdown("---")
        st.markdown("## 📥 Export Your Financial Report")
        st.caption("Download your report as a professional PDF document.")

        try:
            pdf_data = generate_pdf(report)

            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_data,
                file_name="Financial_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

            st.success("✅ PDF is ready to download!")

            st.info(
                "💡 Tip: Generate a report every month to track improvements in your financial health."
            )

        except Exception as e:
            st.error(f"❌ Unable to generate PDF: {e}")

    with side_col:
        render_side_panel(report, goal_summary, key_prefix="dashboard")

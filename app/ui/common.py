"""
Shared styling, session-state, and helper functions used by every page of
the Personal Finance Coach multi-page dashboard.
"""

import streamlit as st

from app.services.llm_client import llm_client
from app.db.database import SessionLocal, init_db
from app.db import crud

PALETTE = [
    "#4f7cff",
    "#22c55e",
    "#f59e0b",
    "#a855f7",
    "#ef4444",
    "#14b8a6",
    "#eab308",
    "#ec4899",
]

_CSS = """
<style>
.fc-card {
    background: #12151c;
    border: 1px solid #262a35;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 14px;
}
.fc-metric-label { color: #9aa0ab; font-size: 0.85rem; margin-bottom: 4px; }
.fc-metric-value { font-size: 1.8rem; font-weight: 700; color: #f2f3f5; }
.fc-delta-up { color: #22c55e; font-size: 0.85rem; }
.fc-delta-down { color: #ef4444; font-size: 0.85rem; }
.fc-section-title { font-size: 1.05rem; font-weight: 700; color: #f2f3f5; margin-bottom: 10px; }
.fc-insight-card { border-radius: 12px; padding: 14px 16px; margin-bottom: 10px; color: #f2f3f5; }
.fc-alloc-card { border-radius: 12px; padding: 14px 16px; color: white; margin-bottom: 10px; }
.fc-bar-track { background: #262a35; border-radius: 6px; height: 8px; width: 100%; margin-top: 4px; }
.fc-bar-fill { border-radius: 6px; height: 8px; }
</style>
"""


def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)


def money(x: float) -> str:
    return f"₹{x:,.0f}"


def pct_delta(curr: float, prev: float | None) -> float | None:
    if not prev:
        return None
    return (curr - prev) / prev * 100


def metric_card(icon: str, label: str, value: str, delta_pct: float | None, caption: str = ""):
    if delta_pct is None:
        delta_html = f'<div class="fc-delta-up">{caption}</div>' if caption else ""
    else:
        cls = "fc-delta-up" if delta_pct >= 0 else "fc-delta-down"
        arrow = "▲" if delta_pct >= 0 else "▼"
        delta_html = f'<div class="{cls}">{arrow} {abs(delta_pct):.1f}% vs previous report</div>'

    st.markdown(
        f"""
        <div class="fc-card">
            <div class="fc-metric-label">{icon} {label}</div>
            <div class="fc-metric-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------
# Session State
# ---------------------------------------------------------------------

def init_session_state():
    if "report" not in st.session_state:
        st.session_state.report = None
        st.session_state.history = []
        st.session_state.chat_messages = []


def load_history(name: str, age: int):
    try:
        init_db()
        session = SessionLocal()

        try:
            user = crud.get_or_create_user(session, name, age)
            records = crud.get_report_history(session, user.id)
            records = list(reversed(records))

            return [
                {
                    "date": r.created_at,
                    "income": r.total_income,
                    "expenses": r.total_expenses,
                    "savings": r.net_savings,
                    "score": r.financial_health_score,
                }
                for r in records
            ]

        finally:
            session.close()

    except Exception:
        return []


def require_report():
    if st.session_state.report is None:
        st.info(
            "No report yet. Use the Dashboard page to generate your first financial report."
        )
        return False

    return True


# ---------------------------------------------------------------------
# Right Panel
# ---------------------------------------------------------------------

def render_side_panel(report, goal_summary: str, key_prefix: str = ""):

    st.markdown(
        '<div class="fc-section-title">✨ AI Agent Recommendations</div>',
        unsafe_allow_html=True,
    )

    with st.expander("💰 Income Agent"):
        st.write(report.income.summary)

    with st.expander("💳 Expense Agent"):
        st.write(report.expenses.summary)

    with st.expander("📈 Investment Agent"):
        st.write(report.investment.summary)
        st.caption(f"Risk approach: {report.investment.risk_analysis}")

    with st.expander("🎯 Goal Agent"):
        st.write(goal_summary)

    st.markdown(
        '<div class="fc-section-title">💬 Ask Finance AI</div>',
        unsafe_allow_html=True,
    )

    if not llm_client.is_live:
        st.info(
            "AI demo mode is active. Configure your Gemini/OpenAI API key in .env."
        )

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    question = st.chat_input(
        "Type your question...",
        key=f"{key_prefix}_chat_input",
    )

    if question:

        st.session_state.chat_messages.append(
            {"role": "user", "content": question}
        )

        greeting = question.strip().lower()

        if greeting in [
            "hi",
            "hello",
            "hey",
            "good morning",
            "good evening",
            "good afternoon",
        ]:

            answer = (
                f"Hi {report.user_name}! 👋\n\n"
                "I'm your Personal Finance AI Assistant.\n\n"
                "You can ask me about:\n"
                "• Budget Planning\n"
                "• Expense Reduction\n"
                "• Saving Money\n"
                "• Investments\n"
                "• Emergency Fund\n"
                "• Financial Goals\n"
                "• Understanding your Financial Report"
            )

        else:

            system_prompt = """
You are Finance AI.

You are a professional personal finance assistant.

Rules:

- Always answer the user's question first.
- Be conversational.
- Keep answers under 120 words.
- Use the financial data ONLY if it helps answer the question.
- Do NOT summarize the user's finances unless asked.
- Give practical suggestions.
"""

            context = f"""
User Financial Information

Name: {report.user_name}

Monthly Income: ₹{report.income.total_monthly_income:.2f}

Monthly Expenses: ₹{report.expenses.total_monthly_expenses:.2f}

Net Monthly Savings: ₹{report.net_monthly_savings:.2f}

Financial Health Score: {report.financial_health_score}/100

User Question:
{question}
"""

            with st.spinner("Thinking..."):
                answer = llm_client.complete(
                    prompt=context,
                    system=system_prompt,
                )

        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        st.rerun()
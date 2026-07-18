"""
Streamlit multi-page dashboard for the Personal Finance Coach system.

Run with:
    streamlit run app/ui/streamlit_app.py
"""

import sys
from pathlib import Path

# Allow running via `streamlit run app/ui/streamlit_app.py` from repo root
sys.path.append(str(Path(__file__).resolve().parents[2]))

import streamlit as st

from app.ui.pages import dashboard, income, expenses, investment, goals
from app.ui.common import init_session_state

st.set_page_config(page_title="Personal Finance Coach", page_icon="💰", layout="wide")
init_session_state()

pages = [
    st.Page(dashboard.render, title="Dashboard", icon="🏠", url_path="dashboard", default=True),
    st.Page(income.render, title="Income", icon="💵", url_path="income"),
    st.Page(expenses.render, title="Expenses", icon="💳", url_path="expenses"),
    st.Page(investment.render, title="Investment", icon="📈", url_path="investment"),
    st.Page(goals.render, title="Goals", icon="🎯", url_path="goals"),
]

nav = st.navigation(pages)

with st.sidebar:
    st.markdown("### 🕘 Report History")
    if st.session_state.history:
        for h in reversed(st.session_state.history[-5:]):
            st.caption(f"{h['date'].strftime('%b %d, %Y %H:%M')} — Score {h['score']}/100")
    else:
        st.caption("Generate a report on the Dashboard page to see history here.")

nav.run()

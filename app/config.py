"""
App-wide configuration, loaded from environment variables (.env).
"""

import os
from dotenv import load_dotenv
try:
    import streamlit as st
    secrets = st.secrets
except Exception:
    secrets = {}

load_dotenv()


class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile"
    )

    LLM_PROVIDER = os.getenv(
        "LLM_PROVIDER",
        "mock"
    ).lower()

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///data/finance.db"
    )

    LOG_LEVEL = os.getenv(
        "LOG_LEVEL",
        "INFO"
    )


settings = Settings()

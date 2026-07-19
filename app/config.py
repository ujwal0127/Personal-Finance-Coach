"""
App-wide configuration, loaded from Streamlit Secrets (deployment)
or .env (local development).
"""

import os
from dotenv import load_dotenv

load_dotenv()

try:
    import streamlit as st
    _secrets = st.secrets
except Exception:
    _secrets = {}


def get_setting(name: str, default: str = ""):
    """Read from Streamlit Secrets first, then environment variables."""
    if name in _secrets:
        return _secrets[name]
    return os.getenv(name, default)


class Settings:
    OPENAI_API_KEY = get_setting("OPENAI_API_KEY", "")
    GOOGLE_API_KEY = get_setting("GOOGLE_API_KEY", "")

    GROQ_API_KEY = get_setting("GROQ_API_KEY", "")
    GROQ_MODEL = get_setting(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile",
    )

    LLM_PROVIDER = get_setting(
        "LLM_PROVIDER",
        "mock",
    ).lower()

    DATABASE_URL = get_setting(
        "DATABASE_URL",
        "sqlite:///data/finance.db",
    )

    LOG_LEVEL = get_setting(
        "LOG_LEVEL",
        "INFO",
    )


settings = Settings()

# ---- Temporary Debug (remove after testing) ----
print("===================================")
print("LLM Provider :", settings.LLM_PROVIDER)
print("Groq Key     :", bool(settings.GROQ_API_KEY))
print("Groq Model   :", settings.GROQ_MODEL)
print("===================================")

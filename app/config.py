"""
App-wide configuration, loaded from environment variables (.env).
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

    # "openai" | "gemini" | "mock"
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock").lower()

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/finance.db")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()

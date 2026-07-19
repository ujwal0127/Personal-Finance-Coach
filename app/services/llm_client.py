"""
LLM client wrapper for Groq, OpenAI and Google Gemini.

Features:
- Supports Groq, OpenAI, Gemini and Mock mode
- Automatic retries for temporary server errors
- Friendly user-facing error messages
- Supports system prompts
"""

from __future__ import annotations

import time

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:

    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self._client = None

        # --------------------------------------------------------
        # OpenAI
        # --------------------------------------------------------
        if self.provider == "openai" and settings.OPENAI_API_KEY:
            try:
                from langchain_openai import ChatOpenAI

                self._client = ChatOpenAI(
                    model="gpt-4o-mini",
                    api_key=settings.OPENAI_API_KEY,
                    temperature=0.4,
                )

                logger.info("LLMClient using OpenAI")

            except Exception as e:
                logger.exception(e)
                self.provider = "mock"

        # --------------------------------------------------------
        # Gemini
        # --------------------------------------------------------
        elif self.provider == "gemini" and settings.GOOGLE_API_KEY:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI

                self._client = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    google_api_key=settings.GOOGLE_API_KEY,
                    temperature=0.4,
                )

                logger.info("LLMClient using Gemini")

            except Exception as e:
                logger.exception(e)
                self.provider = "mock"

        # --------------------------------------------------------
        # Groq
        # --------------------------------------------------------
        elif self.provider == "groq" and settings.GROQ_API_KEY:
            try:
                from langchain_groq import ChatGroq

                self._client = ChatGroq(
                    model=settings.GROQ_MODEL,
                    api_key=settings.GROQ_API_KEY,
                    temperature=0.4,
                )

                logger.info("LLMClient using Groq")

            except Exception as e:
                logger.exception(e)
                raise

        # --------------------------------------------------------
        # Mock
        # --------------------------------------------------------
        else:
            self.provider = "mock"
            logger.info("LLMClient using Mock AI")

    # --------------------------------------------------------
    @property
    def is_live(self):
        return self.provider != "mock" and self._client is not None

    # --------------------------------------------------------
    def complete(self, prompt: str, system: str | None = None):

        if self.provider == "mock":
            return self._mock_complete(prompt)

        messages = []

        if system:
            messages.append(("system", system))

        messages.append(("human", prompt))

        retries = 3

        for attempt in range(retries):

            try:
                response = self._client.invoke(messages)

                if hasattr(response, "content"):
                    return response.content

                return str(response)

            except Exception as e:

                text = str(e)

                # Temporary unavailable
                if "503" in text or "UNAVAILABLE" in text:
                    logger.warning(
                        f"{self.provider.upper()} temporarily unavailable. "
                        f"Retry {attempt + 1}/{retries}"
                    )

                    time.sleep(2)
                    continue

                # Rate limit
                if "429" in text:
                    return (
                        f"⚠️ {self.provider.upper()} API rate limit reached.\n\n"
                        "Please wait a few moments and try again."
                    )

                # Invalid model
                if "404" in text:
                    return (
                        f"⚠️ {self.provider.upper()} model not found.\n\n"
                        "Please verify your configured model name."
                    )

                logger.exception(e)

                return (
                    "⚠️ The AI assistant is temporarily unavailable.\n\n"
                    "Please try again in a few moments."
                )

        return (
            f"⚠️ {self.provider.upper()} servers are currently busy.\n\n"
            "Please try again later."
        )

    # --------------------------------------------------------
    @staticmethod
    def _mock_complete(prompt: str):

        prompt = prompt.lower()

        if "investment" in prompt:
            return (
                "📈 Investment Advice\n\n"
                "Based on your financial profile, consider investing "
                "10–20% of your monthly savings into diversified index "
                "funds or mutual funds while maintaining an emergency fund."
            )

        elif "expense" in prompt or "spending" in prompt:
            return (
                "💳 Expense Analysis\n\n"
                "Your spending appears manageable. Review discretionary "
                "expenses like shopping and entertainment to improve "
                "your monthly savings."
            )

        elif "budget" in prompt:
            return (
                "📊 Budget Recommendation\n\n"
                "Follow the 50/30/20 budgeting rule:\n\n"
                "• 50% Needs\n"
                "• 30% Wants\n"
                "• 20% Savings & Investments"
            )

        elif "goal" in prompt:
            return (
                "🎯 Goal Planning\n\n"
                "Break your financial goal into monthly milestones and "
                "track your progress consistently."
            )

        return (
            "🤖 Personal Finance AI\n\n"
            "Your financial data has been analyzed.\n\n"
            "• Maintain an emergency fund.\n"
            "• Control unnecessary expenses.\n"
            "• Invest consistently.\n"
            "• Review your financial goals every month.\n\n"
            "You're making good progress—keep it up!"
        )


# Singleton
llm_client = LLMClient()

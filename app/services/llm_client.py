"""
LLM client wrapper for OpenAI and Google Gemini.

- Uses LangChain chat models.
- Retries temporary Gemini failures.
- Gives friendly error messages for quota issues.
- Supports system prompts.
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

        if self.provider == "openai" and settings.OPENAI_API_KEY:
            try:
                from langchain_openai import ChatOpenAI

                self._client = ChatOpenAI(
                    model="gpt-4o-mini",
                    api_key=settings.OPENAI_API_KEY,
                    temperature=0.4,
                )

                logger.info("Using OpenAI")

            except Exception as e:
                logger.exception(e)
                self.provider = "mock"

        elif self.provider == "gemini" and settings.GOOGLE_API_KEY:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI

                self._client = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    google_api_key=settings.GOOGLE_API_KEY,
                    temperature=0.4,
                )

                logger.info("Using Gemini")

            except Exception as e:
                logger.exception(e)
                self.provider = "mock"

        else:
            self.provider = "mock"

    @property
    def is_live(self):
        return self.provider != "mock" and self._client is not None

    def complete(self, prompt: str, system: str | None = None):

        if self.provider == "mock":
            return self._mock_complete(prompt)

        messages = []

        if system:
            messages.append(("system", system))

        messages.append(("human", prompt))

        for attempt in range(3):

            try:

                response = self._client.invoke(messages)

                if hasattr(response, "content"):
                    return response.content

                return str(response)

            except Exception as e:

                text = str(e)

                if "503" in text or "UNAVAILABLE" in text:
                    logger.warning("Gemini busy. Retrying...")
                    time.sleep(5)
                    continue

                if "429" in text:
                    return (
                        "⚠️ Gemini API quota has been exceeded.\n\n"
                        "Please wait for the quota to reset or use another API key."
                    )

                if "404" in text:
                    return (
                        "⚠️ Gemini model is unavailable.\n\n"
                        "Please verify the configured model."
                    )

                logger.exception(e)
                return f"AI Error:\n\n{text}"

        return (
            "Gemini servers are currently busy.\n"
            "Please try again in a few minutes."
        )

    @staticmethod
    def _mock_complete(prompt: str):

        first = prompt.splitlines()[0] if prompt else ""

        return (
            f"(Mock AI)\n\n"
            f"I received your request.\n\n"
            f"Prompt starts with:\n{first}"
        )


llm_client = LLMClient()
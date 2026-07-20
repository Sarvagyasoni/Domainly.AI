# from google import genai
# from app.core.config import settings
# class GeminiProvider:
#     def __init__(self):
#         self.client = genai.Client(
#             api_key=settings.GEMINI_API_KEY
#         )
#     # Normal response
#     def generate_response(self, prompt: str):
#         response = self.client.models.generate_content(
#             model="gemini-2.5-flash",
#             contents=prompt
#         )
#         return response.text
#     # Streaming response
#     def stream_response(self, prompt: str):
#         response = self.client.models.generate_content_stream(
#             model="gemini-2.5-flash",
#             contents=prompt
#         )
#         for chunk in response:
#             if chunk.text:
#                 yield chunk.text

import logging
import time

try:
    from google import genai
except ImportError:  # pragma: no cover - depends on environment
    genai = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiProvider:
    """
    Handles all communication with the Gemini API.
    """

    def __init__(self):
        self.client = None
        self.model = settings.GEMINI_MODEL

        if not settings.GEMINI_API_KEY or genai is None:
            logger.warning(
                "Gemini API key not configured or dependency missing. Falling back to offline mode."
            )
            return

        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def _offline_response(self, prompt: str) -> str:
        prompt_preview = prompt[:120].replace("\n", " ").strip()
        return (
            "I’m currently running in offline mode. "
            "Configure GEMINI_API_KEY to enable live AI responses. "
            f"Your request: {prompt_preview}"
        )

    def generate_response(self, prompt: str) -> str:
        """
        Generate a complete response from Gemini.
        """
        if self.client is None:
            return self._offline_response(prompt)

        last_exception = None
        for attempt in range(settings.MAX_RETRIES):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
                return response.text
            except Exception as e:
                last_exception = e
                logger.warning(
                    "Gemini request failed (Attempt %s/%s): %s",
                    attempt + 1,
                    settings.MAX_RETRIES,
                    str(e)
                )
                time.sleep(1)

        logger.exception("Gemini failed after all retry attempts.")
        raise last_exception

    def stream_response(self, prompt: str):
        """
        Stream Gemini response token by token.
        """
        if self.client is None:
            yield self._offline_response(prompt)
            return

        last_exception = None
        for attempt in range(settings.MAX_RETRIES):
            try:
                response = self.client.models.generate_content_stream(
                    model=self.model,
                    contents=prompt,
                )
                for chunk in response:
                    if getattr(chunk, "text", None):
                        yield chunk.text
                return
            except Exception as e:
                last_exception = e
                logger.warning(
                    "Gemini streaming failed (Attempt %s/%s): %s",
                    attempt + 1,
                    settings.MAX_RETRIES,
                    str(e)
                )
                time.sleep(1)

        logger.exception("Gemini streaming failed after all retry attempts.")
        raise last_exception
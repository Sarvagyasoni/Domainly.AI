import unittest

from app.core import config
from app.providers.gemini_provider import GeminiProvider


class GeminiProviderFallbackTests(unittest.TestCase):
    def test_returns_fallback_when_api_key_is_missing(self):
        original_key = config.settings.GEMINI_API_KEY
        config.settings.GEMINI_API_KEY = None

        try:
            provider = GeminiProvider()
            response = provider.generate_response("Hello")
            streamed = list(provider.stream_response("Hello"))
        finally:
            config.settings.GEMINI_API_KEY = original_key

        self.assertIn("offline mode", response.lower())
        self.assertEqual(streamed, [response])


if __name__ == "__main__":
    unittest.main()

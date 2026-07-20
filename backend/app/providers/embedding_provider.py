import logging

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover - depends on environment
    genai = None
    types = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiEmbeddingProvider:
    """Create retrieval embeddings with the configured Gemini model."""

    def __init__(self):
        self.model = settings.EMBEDDING_MODEL
        self.dimensions = settings.EMBEDDING_DIMENSIONS
        self.client = None
        if settings.GEMINI_API_KEY and genai is not None:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    @property
    def available(self) -> bool:
        return self.client is not None

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not self.client or types is None:
            raise RuntimeError("Gemini embeddings are not configured.")
        response = self.client.models.embed_content(
            model=self.model,
            contents=texts,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=self.dimensions,
            ),
        )
        return [embedding.values for embedding in response.embeddings]

    def embed_query(self, text: str) -> list[float]:
        if not self.client or types is None:
            raise RuntimeError("Gemini embeddings are not configured.")
        response = self.client.models.embed_content(
            model=self.model,
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=self.dimensions,
            ),
        )
        return response.embeddings[0].values

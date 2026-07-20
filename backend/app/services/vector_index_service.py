import hashlib
import json
import logging
from pathlib import Path

from app.providers.embedding_provider import GeminiEmbeddingProvider

logger = logging.getLogger(__name__)


class VectorIndexService:
    """Persist and reuse embeddings for local knowledge chunks."""

    INDEX_DIR = Path(__file__).resolve().parent.parent / "storage" / "vector_indexes"

    @staticmethod
    def _fingerprint(texts: list[str], model: str, dimensions: int) -> str:
        payload = json.dumps(
            {"texts": texts, "model": model, "dimensions": dimensions},
            ensure_ascii=False,
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def get_vectors(
        cls,
        domain: str,
        texts: list[str],
        provider: GeminiEmbeddingProvider,
    ) -> list[list[float]]:
        fingerprint = cls._fingerprint(texts, provider.model, provider.dimensions)
        index_path = cls.INDEX_DIR / f"{domain}.json"

        if index_path.exists():
            try:
                saved = json.loads(index_path.read_text(encoding="utf-8"))
                if saved.get("fingerprint") == fingerprint:
                    vectors = saved.get("vectors", [])
                    if len(vectors) == len(texts):
                        return vectors
            except (OSError, json.JSONDecodeError, TypeError):
                logger.warning("Ignoring invalid vector index: %s", index_path)

        vectors = provider.embed_documents(texts)
        if len(vectors) != len(texts):
            raise ValueError("Embedding response did not match the chunk count.")

        cls.INDEX_DIR.mkdir(parents=True, exist_ok=True)
        index_path.write_text(
            json.dumps(
                {
                    "fingerprint": fingerprint,
                    "model": provider.model,
                    "dimensions": provider.dimensions,
                    "vectors": vectors,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return vectors

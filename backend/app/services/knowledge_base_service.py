import math
import re
import logging
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from app.core.config import settings
from app.providers.embedding_provider import GeminiEmbeddingProvider
from app.services.vector_index_service import VectorIndexService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class KnowledgeChunk:
    """A searchable piece of a domain knowledge-base document."""

    domain: str
    source: str
    section: str
    text: str
    tokens: tuple[str, ...]


class KnowledgeBaseService:
    """Load, chunk, rank, and return relevant local knowledge."""

    BASE_DIR = Path(__file__).resolve().parent.parent / "knowledge_base"
    _chunk_cache: ClassVar[dict[str, list[KnowledgeChunk]]] = {}
    embedding_provider: ClassVar[GeminiEmbeddingProvider] = GeminiEmbeddingProvider()

    # Very common terms add noise to lexical retrieval and are ignored.
    STOP_WORDS = {
        "a", "an", "and", "are", "as", "at", "be", "by", "can", "do",
        "for", "from", "how", "i", "in", "is", "it", "me", "my", "of",
        "on", "or", "that", "the", "this", "to", "was", "what", "when",
        "where", "which", "with", "you", "your",
    }

    @classmethod
    def _tokenize(cls, text: str) -> tuple[str, ...]:
        words = re.findall(r"[a-z0-9][a-z0-9+#.-]*", text.lower())
        return tuple(word for word in words if word not in cls.STOP_WORDS)

    @classmethod
    def _split_sections(cls, content: str) -> list[tuple[str, str]]:
        """Split documents at === SECTION === headings."""
        sections: list[tuple[str, str]] = []
        heading = "Overview"
        lines: list[str] = []

        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("===") and stripped.endswith("==="):
                if lines and "\n".join(lines).strip():
                    sections.append((heading, "\n".join(lines).strip()))
                heading = stripped.strip("= ").title()
                lines = []
            else:
                lines.append(line)

        if lines and "\n".join(lines).strip():
            sections.append((heading, "\n".join(lines).strip()))
        return sections

    @classmethod
    def _chunk_section(cls, text: str) -> list[str]:
        """Create fixed-size word chunks with bounded overlap."""
        words = text.split()
        if not words:
            return []

        chunk_size = max(settings.RAG_CHUNK_SIZE, 1)
        overlap = min(max(settings.RAG_CHUNK_OVERLAP, 0), chunk_size - 1)
        step = chunk_size - overlap
        return [
            " ".join(words[index:index + chunk_size])
            for index in range(0, len(words), step)
        ]

    @classmethod
    def _load_chunks(cls, domain: str) -> list[KnowledgeChunk]:
        if domain in cls._chunk_cache:
            return cls._chunk_cache[domain]

        file_path = cls.BASE_DIR / f"{domain}.txt"
        if not file_path.exists():
            cls._chunk_cache[domain] = []
            return []

        content = file_path.read_text(encoding="utf-8").strip()
        chunks: list[KnowledgeChunk] = []
        for section, section_text in cls._split_sections(content):
            for text in cls._chunk_section(section_text):
                chunks.append(
                    KnowledgeChunk(
                        domain=domain,
                        source=file_path.name,
                        section=section,
                        text=text,
                        tokens=cls._tokenize(f"{section} {text}"),
                    )
                )

        cls._chunk_cache[domain] = chunks
        return chunks

    @classmethod
    def retrieve(
        cls,
        domain: str,
        query: str,
        top_k: int | None = None,
    ) -> list[KnowledgeChunk]:
        """Combine semantic vector similarity and BM25 lexical relevance."""
        chunks = cls._load_chunks(domain)
        query_tokens = set(cls._tokenize(query))
        if not chunks or not query_tokens:
            return []

        lexical_scores = cls._bm25_scores(chunks, query_tokens)
        vector_scores = cls._vector_scores(domain, chunks, query)

        max_lexical = max(lexical_scores.values(), default=0.0)
        vector_weight = min(max(settings.RAG_VECTOR_WEIGHT, 0.0), 1.0)
        combined: list[tuple[float, KnowledgeChunk]] = []

        for index, chunk in enumerate(chunks):
            lexical = lexical_scores.get(index, 0.0)
            normalized_lexical = lexical / max_lexical if max_lexical else 0.0
            vector = vector_scores.get(index, 0.0)

            # With embeddings enabled, weak semantic matches do not retrieve
            # arbitrary content. Exact BM25 matches remain eligible.
            if lexical <= 0 and vector < settings.RAG_VECTOR_MIN_SCORE:
                continue
            if vector_scores:
                score = (
                    vector_weight * max(vector, 0.0)
                    + (1 - vector_weight) * normalized_lexical
                )
            else:
                score = normalized_lexical
            combined.append((score, chunk))

        limit = top_k if top_k is not None else settings.RAG_TOP_K
        combined.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in combined[:limit]]

    @classmethod
    def _bm25_scores(
        cls,
        chunks: list[KnowledgeChunk],
        query_tokens: set[str],
    ) -> dict[int, float]:
        """Return BM25 scores keyed by chunk position."""

        document_frequencies = Counter(
            token
            for chunk in chunks
            for token in set(chunk.tokens)
        )
        average_length = sum(len(chunk.tokens) for chunk in chunks) / len(chunks)
        k1 = 1.5
        b = 0.75
        scored: dict[int, float] = {}

        for index, chunk in enumerate(chunks):
            frequencies = Counter(chunk.tokens)
            score = 0.0
            for token in query_tokens:
                frequency = frequencies[token]
                if not frequency:
                    continue
                documents_with_token = document_frequencies[token]
                inverse_document_frequency = math.log(
                    1 + (len(chunks) - documents_with_token + 0.5)
                    / (documents_with_token + 0.5)
                )
                length_normalization = frequency + k1 * (
                    1 - b + b * len(chunk.tokens) / max(average_length, 1)
                )
                score += inverse_document_frequency * (
                    frequency * (k1 + 1) / length_normalization
                )
            if score > 0:
                scored[index] = score
        return scored

    @staticmethod
    def _cosine_similarity(left: list[float], right: list[float]) -> float:
        if len(left) != len(right) or not left:
            return 0.0
        dot_product = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))
        if not left_norm or not right_norm:
            return 0.0
        return dot_product / (left_norm * right_norm)

    @classmethod
    def _vector_scores(
        cls,
        domain: str,
        chunks: list[KnowledgeChunk],
        query: str,
    ) -> dict[int, float]:
        provider = cls.embedding_provider
        if not provider.available:
            return {}
        try:
            texts = [f"{chunk.section}\n{chunk.text}" for chunk in chunks]
            vectors = VectorIndexService.get_vectors(domain, texts, provider)
            query_vector = provider.embed_query(query)
            return {
                index: cls._cosine_similarity(query_vector, vector)
                for index, vector in enumerate(vectors)
            }
        except Exception as error:
            logger.warning(
                "Vector retrieval failed for %s; using BM25 fallback: %s",
                domain,
                error,
            )
            return {}

    @classmethod
    def format_context(cls, chunks: list[KnowledgeChunk]) -> str:
        return "\n\n".join(
            f"[Source: {chunk.source} | Section: {chunk.section}]\n{chunk.text}"
            for chunk in chunks
        )

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached chunks, primarily for tests and live content updates."""
        cls._chunk_cache.clear()

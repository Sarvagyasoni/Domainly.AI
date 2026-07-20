import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from app.core.config import settings


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
        """Rank chunks with BM25 and return the most relevant results."""
        chunks = cls._load_chunks(domain)
        query_tokens = set(cls._tokenize(query))
        if not chunks or not query_tokens:
            return []

        document_frequencies = Counter(
            token
            for chunk in chunks
            for token in set(chunk.tokens)
        )
        average_length = sum(len(chunk.tokens) for chunk in chunks) / len(chunks)
        k1 = 1.5
        b = 0.75
        scored: list[tuple[float, KnowledgeChunk]] = []

        for chunk in chunks:
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
                scored.append((score, chunk))

        limit = top_k if top_k is not None else settings.RAG_TOP_K
        scored.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in scored[:limit]]

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

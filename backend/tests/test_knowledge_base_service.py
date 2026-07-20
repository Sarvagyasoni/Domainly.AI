import tempfile
import unittest
from pathlib import Path

from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.vector_index_service import VectorIndexService


class FakeEmbeddingProvider:
    available = True
    model = "fake-embedding-model"
    dimensions = 2

    def __init__(self):
        self.document_calls = 0

    def embed_documents(self, texts):
        self.document_calls += 1
        return [
            [1.0, 0.0] if "Retention" in text else [0.0, 1.0]
            for text in texts
        ]

    def embed_query(self, text):
        return [1.0, 0.0]


class OfflineEmbeddingProvider:
    available = False


class KnowledgeBaseServiceTests(unittest.TestCase):
    def setUp(self):
        self.original_base_dir = KnowledgeBaseService.BASE_DIR
        self.original_provider = KnowledgeBaseService.embedding_provider
        self.original_index_dir = VectorIndexService.INDEX_DIR
        self.temp_directory = tempfile.TemporaryDirectory()
        KnowledgeBaseService.BASE_DIR = Path(self.temp_directory.name)
        KnowledgeBaseService.embedding_provider = OfflineEmbeddingProvider()
        VectorIndexService.INDEX_DIR = Path(self.temp_directory.name) / "indexes"
        KnowledgeBaseService.clear_cache()

    def tearDown(self):
        KnowledgeBaseService.BASE_DIR = self.original_base_dir
        KnowledgeBaseService.embedding_provider = self.original_provider
        VectorIndexService.INDEX_DIR = self.original_index_dir
        KnowledgeBaseService.clear_cache()
        self.temp_directory.cleanup()

    def _write_knowledge(self, content: str) -> None:
        (KnowledgeBaseService.BASE_DIR / "programming.txt").write_text(
            content,
            encoding="utf-8",
        )

    def test_retrieves_the_section_matching_the_query(self):
        self._write_knowledge(
            """=== DATABASES ===
Indexes make repeated database lookups faster.

=== ASYNC PYTHON ===
Asyncio helps with concurrent network requests and other I/O work.

=== TESTING ===
Unit tests verify one isolated behavior.
"""
        )

        chunks = KnowledgeBaseService.retrieve(
            "programming",
            "How should I use asyncio for network concurrency?",
            top_k=1,
        )

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].section, "Async Python")
        self.assertIn("network requests", chunks[0].text)

    def test_returns_no_chunks_when_domain_file_is_missing(self):
        chunks = KnowledgeBaseService.retrieve(
            "missing-domain",
            "Any question",
        )

        self.assertEqual(chunks, [])

    def test_formatted_context_contains_source_metadata(self):
        self._write_knowledge(
            """=== SECURITY ===
Parameterized queries help prevent SQL injection.
"""
        )
        chunks = KnowledgeBaseService.retrieve(
            "programming",
            "SQL injection queries",
        )

        context = KnowledgeBaseService.format_context(chunks)

        self.assertIn("Source: programming.txt", context)
        self.assertIn("Section: Security", context)

    def test_vector_search_finds_semantic_match_without_shared_words(self):
        self._write_knowledge(
            """=== RETENTION ===
Churn measures the rate at which subscribers cancel a product.

=== ASYNC PYTHON ===
Asyncio coordinates concurrent I/O operations.
"""
        )
        provider = FakeEmbeddingProvider()
        KnowledgeBaseService.embedding_provider = provider

        chunks = KnowledgeBaseService.retrieve(
            "programming",
            "Why are my customers disappearing?",
            top_k=1,
        )

        self.assertEqual(chunks[0].section, "Retention")
        self.assertEqual(provider.document_calls, 1)

        KnowledgeBaseService.retrieve(
            "programming",
            "People keep abandoning the service",
            top_k=1,
        )
        self.assertEqual(provider.document_calls, 1)


if __name__ == "__main__":
    unittest.main()

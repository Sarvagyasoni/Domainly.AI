import tempfile
import unittest
from pathlib import Path

from app.services.knowledge_base_service import KnowledgeBaseService


class KnowledgeBaseServiceTests(unittest.TestCase):
    def setUp(self):
        self.original_base_dir = KnowledgeBaseService.BASE_DIR
        self.temp_directory = tempfile.TemporaryDirectory()
        KnowledgeBaseService.BASE_DIR = Path(self.temp_directory.name)
        KnowledgeBaseService.clear_cache()

    def tearDown(self):
        KnowledgeBaseService.BASE_DIR = self.original_base_dir
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


if __name__ == "__main__":
    unittest.main()

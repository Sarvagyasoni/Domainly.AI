import tempfile
import unittest
from pathlib import Path

from app.repositories.conversation_repository import ConversationRepository
from app.services.chat_service import ChatService
from app.services.knowledge_base_service import KnowledgeBaseService


class FakeChatProvider:
    def generate_response(self, prompt):
        return "A stored complete response."

    def stream_response(self, prompt):
        yield "A stored "
        yield "streamed response."


class OfflineEmbeddingProvider:
    available = False


class ConversationDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        database = Path(self.temp_directory.name) / "test.db"
        self.repository = ConversationRepository(database=database)
        self.original_embedding_provider = KnowledgeBaseService.embedding_provider
        KnowledgeBaseService.embedding_provider = OfflineEmbeddingProvider()

    def tearDown(self):
        KnowledgeBaseService.embedding_provider = self.original_embedding_provider
        self.temp_directory.cleanup()

    def test_crud_messages_title_and_domain_filter(self):
        programming = self.repository.create("programming")
        gaming = self.repository.create("gaming")

        updated = self.repository.add_message(
            programming.id,
            "user",
            "Explain database indexes clearly",
        )
        self.repository.add_message(
            programming.id,
            "assistant",
            "An index speeds up selected reads.",
        )

        self.assertEqual(updated.title, "Explain database indexes clearly")
        self.assertEqual(len(self.repository.get_by_id(programming.id).messages), 2)
        self.assertEqual(
            [conversation.id for conversation in self.repository.get_by_domain("gaming")],
            [gaming.id],
        )
        self.assertTrue(self.repository.delete(programming.id))
        self.assertIsNone(self.repository.get_by_id(programming.id))
        self.assertFalse(self.repository.delete("missing"))

    def test_normal_and_streaming_chat_responses_are_persisted(self):
        service = ChatService(
            provider=FakeChatProvider(),
            conversations=self.repository,
        )
        normal_chat = self.repository.create("programming")
        response = service.process_chat(
            "programming",
            "What is SQLite?",
            [],
            normal_chat.id,
        )

        self.assertTrue(response["success"])
        self.assertEqual(response["chat_id"], normal_chat.id)
        self.assertEqual(
            [message.role for message in self.repository.get_by_id(normal_chat.id).messages],
            ["user", "assistant"],
        )

        stream_chat = self.repository.create("programming")
        streamed = "".join(
            service.stream_chat(
                "programming",
                "Explain a transaction",
                [],
                stream_chat.id,
            )
        )
        stored = self.repository.get_by_id(stream_chat.id)
        self.assertEqual(streamed, "A stored streamed response.")
        self.assertEqual(stored.messages[-1].content, streamed)


if __name__ == "__main__":
    unittest.main()

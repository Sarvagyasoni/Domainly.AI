from app.repositories.conversation_repository import ConversationRepository
from app.domain_registry.domain_registry import AVAILABLE_DOMAINS

class ConversationService:
    def __init__(self):
        self.repository = ConversationRepository()

    def create_chat(self, domain: str):
        if domain not in AVAILABLE_DOMAINS:
            raise ValueError("Invalid domain.")
        return self.repository.create(domain)

    def get_all_chats(self, domain: str | None = None):
        return self.repository.get_all(domain=domain)

    def get_chat(self, chat_id: str):
        return self.repository.get_by_id(chat_id)

    def delete_chat(self, chat_id: str):
        return self.repository.delete(chat_id)

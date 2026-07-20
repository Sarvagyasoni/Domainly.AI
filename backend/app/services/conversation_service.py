from app.repositories.conversation_repository import ConversationRepository

class ConversationService:
    def __init__(self):
        self.repository = ConversationRepository()

    def create_chat(self, domain: str):
        return self.repository.create(domain)

    def get_all_chats(self):
        return self.repository.get_all()

    def get_chat(self, chat_id: str):
        return self.repository.get_by_id(chat_id)

    def delete_chat(self, chat_id: str):
        self.repository.delete(chat_id)
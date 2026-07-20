import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from app.models.conversation import Conversation, Message
class ConversationRepository:
    """
    Handles all conversation storage operations.
    This class should ONLY deal with reading/writing
    conversation data.
    """
    DATABASE = Path(__file__).resolve().parent.parent / "storage" / "conversations.json"
    def __init__(self):
        self.DATABASE.parent.mkdir(exist_ok=True)
        if not self.DATABASE.exists():
            self.DATABASE.write_text("[]", encoding="utf-8")
    # -------------------------------------------------
    # Internal Helpers
    # -------------------------------------------------
    def _load(self) -> List[dict]:
        with open(self.DATABASE, "r", encoding="utf-8") as file:
            return json.load(file)
    def _save(self, conversations: List[dict]) -> None:
        with open(self.DATABASE, "w", encoding="utf-8") as file:
            json.dump(conversations, file, indent=4)
    # -------------------------------------------------
    # CRUD
    # -------------------------------------------------
    def create(self, domain: str) -> Conversation:
        conversation = Conversation(
            id=str(uuid.uuid4()),
            domain=domain
        )
        conversations = self._load()
        conversations.append(
            conversation.model_dump(mode="json")
        )
        self._save(conversations)
        return conversation
    def get_all(self) -> List[Conversation]:
        return [
            Conversation(**conversation)
            for conversation in self._load()
        ]
    def get_by_id(
        self,
        conversation_id: str
    ) -> Optional[Conversation]:
        for conversation in self._load():
            if conversation["id"] == conversation_id:
                return Conversation(**conversation)
        return None
    def update(
        self,
        conversation: Conversation
    ) -> Conversation:
        conversations = self._load()
        for index, existing in enumerate(conversations):
            if existing["id"] == conversation.id:
                conversation.updated_at = datetime.utcnow()
                conversations[index] = conversation.model_dump(
                    mode="json"
                )
                self._save(conversations)
                return conversation
        raise ValueError("Conversation not found.")
    def delete(
        self,
        conversation_id: str
    ) -> bool:
        conversations = self._load()
        new_conversations = [
            conversation
            for conversation in conversations
            if conversation["id"] != conversation_id
        ]
        if len(new_conversations) == len(conversations):
            return False
        self._save(new_conversations)
        return True
    # -------------------------------------------------
    # Message Operations
    # -------------------------------------------------
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str
    ) -> Conversation:
        conversation = self.get_by_id(conversation_id)
        if conversation is None:
            raise ValueError("Conversation not found.")
        conversation.messages.append(
            Message(
                role=role,
                content=content
            )
        )
        return self.update(conversation)
    # -------------------------------------------------
    # Domain Operations
    # -------------------------------------------------
    def get_by_domain(
        self,
        domain: str
    ) -> List[Conversation]:
        return [
            conversation
            for conversation in self.get_all()
            if conversation.domain == domain
        ]

from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
class Message(BaseModel):
    """
    Represents a single message in a conversation.
    """
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
class Conversation(BaseModel):
    """
    Represents an entire conversation.
    """
    id: str
    title: str = "New Chat"
    domain: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    messages: List[Message] = Field(default_factory=list)
    summary: Optional[str] = None
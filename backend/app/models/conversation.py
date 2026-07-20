from datetime import datetime, timezone
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
class Message(BaseModel):
    """
    Represents a single message in a conversation.
    """
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
class Conversation(BaseModel):
    """
    Represents an entire conversation.
    """
    id: str
    title: str = "New Chat"
    domain: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    messages: List[Message] = Field(default_factory=list)
    summary: Optional[str] = None

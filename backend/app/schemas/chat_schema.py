from pydantic import BaseModel, Field
from typing import List, Optional
class ChatMessage(BaseModel):
    role: str
    content: str
class ChatRequest(BaseModel):
    chat_id: Optional[str] = None
    domain: str
    message: str
    history: List[ChatMessage] = Field(default_factory=list)
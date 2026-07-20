from fastapi import APIRouter
from app.services.conversation_service import ConversationService
router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"]
)
conversation_service = ConversationService()
@router.post("")
def create_chat(domain: str):
    return conversation_service.create_chat(domain)
@router.get("")
def get_all_chats():
    return conversation_service.get_all_chats()
@router.get("/{chat_id}")
def get_chat(chat_id: str):
    return conversation_service.get_chat(chat_id)
@router.delete("/{chat_id}")
def delete_chat(chat_id: str):
    conversation_service.delete_chat(chat_id)
    return {
        "success": True
    }
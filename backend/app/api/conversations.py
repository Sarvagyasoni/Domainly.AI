from fastapi import APIRouter, HTTPException, Query
from app.services.conversation_service import ConversationService
router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"]
)
conversation_service = ConversationService()
@router.post("")
def create_chat(domain: str):
    try:
        return conversation_service.create_chat(domain)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
@router.get("")
def get_all_chats(domain: str | None = Query(default=None)):
    return conversation_service.get_all_chats(domain=domain)
@router.get("/{chat_id}")
def get_chat(chat_id: str):
    conversation = conversation_service.get_chat(chat_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conversation
@router.delete("/{chat_id}")
def delete_chat(chat_id: str):
    if not conversation_service.delete_chat(chat_id):
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"success": True}

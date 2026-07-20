from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas.chat_schema import ChatRequest
from app.services.chat_service import ChatService
router = APIRouter()
chat_service = ChatService()
# Existing endpoint
@router.post("/chat")
def chat(request: ChatRequest):
    return chat_service.process_chat(
        request.domain,
        request.message,
        request.history,
        request.chat_id,
    )
# New streaming endpoint
@router.post("/chat/stream")
def chat_stream(request: ChatRequest):
    return StreamingResponse(
        chat_service.stream_chat(
            request.domain,
            request.message,
            request.history,
            request.chat_id,
        ),
        media_type="text/plain"
    )

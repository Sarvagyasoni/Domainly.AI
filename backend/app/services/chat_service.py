import logging
from app.builders.prompt_builder import PromptBuilder
from app.domain_registry.domain_registry import AVAILABLE_DOMAINS
from app.providers.gemini_provider import GeminiProvider
from app.services.knowledge_base_service import KnowledgeBaseService
from app.repositories.conversation_repository import ConversationRepository
logger = logging.getLogger(__name__)
class ChatService:
    """
    Handles all chatbot business logic:
    validate domain -> load knowledge base -> build prompt ->
    call Gemini -> log the outcome.
    """
    INVALID_DOMAIN_MESSAGE = "Invalid Domain"
    AI_UNAVAILABLE_MESSAGE = (
        "⚠️ Gemini is currently unavailable. Please try again in a few seconds."
    )
    def __init__(
        self,
        provider=None,
        conversations: ConversationRepository | None = None,
    ):
        self.provider = provider or GeminiProvider()
        self.conversations = conversations or ConversationRepository()
    # ---------------------------------------------------------
    # Private Methods
    # ---------------------------------------------------------
    def _is_valid_domain(self, domain: str) -> bool:
        return domain in AVAILABLE_DOMAINS
    def _build_prompt(
        self,
        domain: str,
        message: str,
        history: list,
    ) -> str:
        chunks = KnowledgeBaseService.retrieve(domain, message)
        knowledge = KnowledgeBaseService.format_context(chunks)
        if chunks:
            logger.info(
                "Retrieved %s knowledge chunks for domain: %s",
                len(chunks),
                domain,
            )
        else:
            logger.info("No relevant knowledge found for domain: %s", domain)
        return PromptBuilder.build(
            domain,
            message,
            history,
            knowledge,
        )
    def _resolve_conversation(self, domain: str, chat_id: str | None):
        if chat_id is None:
            return self.conversations.create(domain)
        conversation = self.conversations.get_by_id(chat_id)
        if conversation is None:
            raise ValueError("Conversation not found.")
        if conversation.domain != domain:
            raise ValueError("Conversation domain does not match the request.")
        return conversation
    # ---------------------------------------------------------
    # Public Methods
    # ---------------------------------------------------------
    def process_chat(
        self,
        domain: str,
        message: str,
        history: list,
        chat_id: str | None = None,
    ):
        logger.info("Chat request received for domain: %s", domain)
        if not self._is_valid_domain(domain):
            logger.warning("Invalid domain requested: %s", domain)
            return {
                "success": False,
                "error": self.INVALID_DOMAIN_MESSAGE,
            }
        try:
            conversation = self._resolve_conversation(domain, chat_id)
        except ValueError as error:
            return {"success": False, "error": str(error)}
        stored_history = conversation.messages or history
        prompt = self._build_prompt(
            domain,
            message,
            stored_history,
        )
        self.conversations.add_message(conversation.id, "user", message)
        try:
            reply = self.provider.generate_response(prompt)
            self.conversations.add_message(conversation.id, "assistant", reply)
            logger.info("Gemini responded successfully for domain: %s", domain)
            return {
                "success": True,
                "domain": domain,
                "chat_id": conversation.id,
                "reply": reply,
            }
        except Exception:
            logger.exception("Error while generating Gemini response.")
            return {
                "success": False,
                "domain": domain,
                "reply": self.AI_UNAVAILABLE_MESSAGE,
            }
    def stream_chat(
        self,
        domain: str,
        message: str,
        history: list,
        chat_id: str | None = None,
    ):
        logger.info("Streaming chat request received for domain: %s", domain)
        if not self._is_valid_domain(domain):
            logger.warning("Invalid streaming domain: %s", domain)
            yield self.INVALID_DOMAIN_MESSAGE
            return
        try:
            conversation = self._resolve_conversation(domain, chat_id)
        except ValueError as error:
            yield str(error)
            return
        stored_history = conversation.messages or history
        prompt = self._build_prompt(
            domain,
            message,
            stored_history,
        )
        self.conversations.add_message(conversation.id, "user", message)
        reply_parts: list[str] = []
        try:
            for chunk in self.provider.stream_response(prompt):
                reply_parts.append(chunk)
                yield chunk
            reply = "".join(reply_parts).strip()
            if reply:
                self.conversations.add_message(
                    conversation.id,
                    "assistant",
                    reply,
                )
            logger.info("Gemini streaming completed for domain: %s", domain)
        except Exception:
            logger.exception("Streaming failed.")
            yield self.AI_UNAVAILABLE_MESSAGE

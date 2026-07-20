import logging
from app.builders.prompt_builder import PromptBuilder
from app.domain_registry.domain_registry import AVAILABLE_DOMAINS
from app.providers.gemini_provider import GeminiProvider
from app.services.knowledge_base_service import KnowledgeBaseService
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
    def __init__(self):
        self.provider = GeminiProvider()
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
        knowledge = KnowledgeBaseService.get_knowledge(domain)
        if knowledge:
            logger.info("Knowledge base loaded for domain: %s", domain)
        else:
            logger.info("No knowledge base file found for domain: %s", domain)
        return PromptBuilder.build(
            domain,
            message,
            history,
            knowledge,
        )
    # ---------------------------------------------------------
    # Public Methods
    # ---------------------------------------------------------
    def process_chat(
        self,
        domain: str,
        message: str,
        history: list,
    ):
        logger.info("Chat request received for domain: %s", domain)
        if not self._is_valid_domain(domain):
            logger.warning("Invalid domain requested: %s", domain)
            return {
                "success": False,
                "error": self.INVALID_DOMAIN_MESSAGE,
            }
        prompt = self._build_prompt(
            domain,
            message,
            history,
        )
        try:
            reply = self.provider.generate_response(prompt)
            logger.info("Gemini responded successfully for domain: %s", domain)
            return {
                "success": True,
                "domain": domain,
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
    ):
        logger.info("Streaming chat request received for domain: %s", domain)
        if not self._is_valid_domain(domain):
            logger.warning("Invalid streaming domain: %s", domain)
            yield self.INVALID_DOMAIN_MESSAGE
            return
        prompt = self._build_prompt(
            domain,
            message,
            history,
        )
        try:
            yield from self.provider.stream_response(prompt)
            logger.info("Gemini streaming completed for domain: %s", domain)
        except Exception:
            logger.exception("Streaming failed.")
            yield self.AI_UNAVAILABLE_MESSAGE
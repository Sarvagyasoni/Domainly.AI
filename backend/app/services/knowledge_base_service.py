from pathlib import Path


class KnowledgeBaseService:
    """
    Loads reference text for a given domain from the
    knowledge_base/ folder and hands it to ChatService,
    which passes it into PromptBuilder.

    Simple RAG version: no chunking, no embeddings, no vector
    search - just read the whole file that matches the domain.
    """

    BASE_DIR = Path(__file__).resolve().parent.parent / "knowledge_base"
    _cache = {}

    @classmethod
    def get_knowledge(cls, domain: str) -> str:
        if domain in cls._cache:
            return cls._cache[domain]

        file_path = cls.BASE_DIR / f"{domain}.txt"

        if not file_path.exists():
            cls._cache[domain] = ""
            return ""

        content = file_path.read_text(encoding="utf-8").strip()
        cls._cache[domain] = content
        return content

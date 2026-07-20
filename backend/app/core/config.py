from dotenv import load_dotenv
import os
# Load environment variables
load_dotenv()
class Settings:
    """
    Central application configuration.
    Every configurable value used throughout the project
    should be defined here instead of being hardcoded
    in service or provider files.
    """
    # ==========================================================
    # Application
    # ==========================================================
    PROJECT_NAME = "Domainly.ai"
    API_VERSION = "v1"
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    # ==========================================================
    # Gemini Configuration
    # ==========================================================
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash"
    )
    # ==========================================================
    # AI Generation Configuration
    # ==========================================================
    TEMPERATURE = float(
        os.getenv("TEMPERATURE", 0.7)
    )
    TOP_P = float(
        os.getenv("TOP_P", 0.95)
    )
    TOP_K = int(
        os.getenv("TOP_K", 40)
    )
    MAX_OUTPUT_TOKENS = int(
        os.getenv("MAX_OUTPUT_TOKENS", 2048)
    )
    # ==========================================================
    # API Configuration
    # ==========================================================
    REQUEST_TIMEOUT = int(
        os.getenv("REQUEST_TIMEOUT", 30)
    )
    MAX_RETRIES = int(
        os.getenv("MAX_RETRIES", 3)
    )
    # ==========================================================
    # Local RAG Configuration
    # ==========================================================
    RAG_TOP_K = int(
        os.getenv("RAG_TOP_K", 3)
    )
    RAG_CHUNK_SIZE = int(
        os.getenv("RAG_CHUNK_SIZE", 180)
    )
    RAG_CHUNK_OVERLAP = int(
        os.getenv("RAG_CHUNK_OVERLAP", 30)
    )
    RAG_VECTOR_WEIGHT = float(
        os.getenv("RAG_VECTOR_WEIGHT", 0.7)
    )
    RAG_VECTOR_MIN_SCORE = float(
        os.getenv("RAG_VECTOR_MIN_SCORE", 0.35)
    )
    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL", "gemini-embedding-001"
    )
    EMBEDDING_DIMENSIONS = int(
        os.getenv("EMBEDDING_DIMENSIONS", 768)
    )
    # ==========================================================
    # Frontend
    # ==========================================================
    FRONTEND_URL = os.getenv(
        "FRONTEND_URL",
        "http://localhost:5173"
    )
settings = Settings()
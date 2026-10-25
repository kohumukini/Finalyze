import os
from edgar import set_identity
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency in local dev
    def load_dotenv(*args, **kwargs):
        return False


load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

# SEC Identity
SEC_FIRST = os.getenv('IDENTITY_FIRST')
SEC_LAST = os.getenv('IDENTITY_LAST')
SEC_EMAIL = os.getenv('IDENTITY_EMAIL')

# LLM model
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_CHAT_MODEL", "openai/gpt-oss-120b")
GROQ_GATEKEEPER_MODEL = os.getenv("HELPER_MODEL", "openai/gpt-oss-20b")

# Embedding Model (Gemini API)
GOOGLE_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2")
# Single source of truth: sizes the pgvector column AND the Gemini output_dimensionality.
# Changing it requires dropping document_chunks and re-ingesting.
EMBEDDING_DIMENSIONS = 768

# RAG Configurations
MAX_CHUNK_SIZE = 500
OVERLAP_SIZE = 100
MAX_DISTANCE = 0.3

# Rate limiting
RATE_LIMIT = os.getenv("RATE_LIMIT", "5/minute")

# CORS
# Provide a comma-separated list in the env (or '*' for all origins)
CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS") or os.getenv("CORS_ALLOWED_ORIGINS", "*")

# Model generation defaults
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.1"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "3000"))

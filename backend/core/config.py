import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency in local dev
    def load_dotenv(*args, **kwargs):
        return False


load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

# LLM models
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Primary Chatting Model
GROQ_MODEL = os.getenv("GROQ_CHAT_MODEL", "openai/gpt-oss-120b")

# Binary Decision & Query Re-writes
GROQ_HELPER_MODEL = os.getenv("HELPER_MODEL", "llama-3.1-8b-instant")

# Embedding Model
MODEL_VECTOR_SIZE = 384

# RAG Configurations
MAX_CHUNK_SIZE = 500
OVERLAP_SIZE = 100
CHAT_HISTORY_LIMIT = 10

# Rate limiting
RATE_LIMIT = os.getenv("RATE_LIMIT", "5/minute")

# CORS
# Provide a comma-separated list in the env (or '*' for all origins)
CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "*")

# Model generation defaults
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.1"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))

# Hugging Face
HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_ACCESS_TOKEN")
HUGGING_FACE_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
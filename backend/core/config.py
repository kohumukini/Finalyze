import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency in local dev
    def load_dotenv(*args, **kwargs):
        return False


load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

# LLM model
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "openai/gpt-oss-120b"

# Embedding Model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MODEL_VECTOR_SIZE = 384

# RAG Configurations
MAX_CHUNK_SIZE = 500
MIN_CHUNK_SIZE = 125
OVERLAP_SIZE = 100

# Rate limiting
RATE_LIMIT = os.getenv("RATE_LIMIT", "5/minute")

# CORS
# Provide a comma-separated list in the env (or '*' for all origins)
CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "*")

# Model generation defaults
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.1"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))

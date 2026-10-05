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
GROQ_MODEL = os.getenv("GROQ_CHAT_MODEL", "openai/gpt-oss-120b")

# Embedding Model (served by the HuggingFace Inference API, not run locally)
# HUGGGING_FACE_ACCESS_TOKEN is kept as a fallback for the original misspelled .env key
HF_TOKEN = os.getenv("HUGGING_FACE_ACCESS_TOKEN") or os.getenv("HUGGGING_FACE_ACCESS_TOKEN")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
HF_EMBEDDING_URL = f"https://router.huggingface.co/hf-inference/models/{EMBEDDING_MODEL}/pipeline/feature-extraction"
MODEL_VECTOR_SIZE = 384

# RAG Configurations
MAX_CHUNK_SIZE = 500
MIN_CHUNK_SIZE = 125
OVERLAP_SIZE = 100

# Rate limiting
RATE_LIMIT = os.getenv("RATE_LIMIT", "5/minute")

# CORS
# Provide a comma-separated list in the env (or '*' for all origins)
CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS") or os.getenv("CORS_ALLOWED_ORIGINS", "*")

# Model generation defaults
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.1"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))

import os
from dotenv import load_dotenv

load_dotenv()

# LLM model
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

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
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "300"))
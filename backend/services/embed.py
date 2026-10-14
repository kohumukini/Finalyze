from google import genai
from google.genai import types

from ..core.config import EMBEDDING_DIMENSIONS, EMBEDDING_MODEL, GOOGLE_KEY
from ..core.logger import get_logger

logger = get_logger(__name__)

# 32 max-size chunks (500 chars each) measure ~3.6k tokens, under the 4k-per-request budget.
# The API itself rejects more than 100 inputs per request.
BATCH_SIZE = 32

_gemini_client: genai.Client | None = None

def _get_gemini_client() -> genai.Client:
    global _gemini_client
    if _gemini_client is None:
        if not GOOGLE_KEY:
            logger.error("Gemini client failed to load")
            raise RuntimeError("GEMINI API KEY NOT FOUND\n")

        _gemini_client = genai.Client(
            api_key=GOOGLE_KEY,
            http_options=types.HttpOptions( #
                timeout=10_000,  # milliseconds. How long the client is willing to wait. 10 seconds per try
                retry_options=types.HttpRetryOptions(attempts=3), # Willing to retry 3 times
            ),
        )
        logger.info("Gemini client successfully loaded")
    return _gemini_client

def embed_chunks(texts: list[str]) -> list[list[float]]:
    """Embed each text into one EMBEDDING_DIMENSIONS-long vector, in input order."""
    if any(not text.strip() for text in texts):
        raise ValueError("embed_chunks received an empty or whitespace-only text")

    client = _get_gemini_client()
    vectors: list[list[float]] = []
    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start:start + BATCH_SIZE]
        # gemini-embedding-2 merges a plain list of strings into ONE vector;
        # wrapping each text in its own Content yields one vector per text.
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=[types.Content(parts=[types.Part(text=text)]) for text in batch],
            config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
        )

        embeddings = response.embeddings
        if embeddings is None or len(embeddings) != len(batch):
            logger.error("Embedding count mismatch for batch starting at %d", start)
            raise RuntimeError(
                f"Expected {len(batch)} embeddings, got {None if embeddings is None else len(embeddings)}"
            )
        for embedding in embeddings:
            if embedding.values is None or len(embedding.values) != EMBEDDING_DIMENSIONS:
                logger.error("Embedding has wrong shape for batch starting at %d", start)
                raise RuntimeError(f"Expected {EMBEDDING_DIMENSIONS}-dimension embedding")
            vectors.append(embedding.values)
    return vectors

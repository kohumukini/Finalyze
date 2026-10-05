import time
from typing import Union

import httpx

from ..core.config import HF_EMBEDDING_URL, HF_TOKEN, MODEL_VECTOR_SIZE
from ..core.logger import get_logger

logger = get_logger(__name__)

BATCH_SIZE = 32
MAX_ATTEMPTS = 4
RETRY_STATUS = {429, 500, 502, 503, 504}  # 503 = HF is still loading the model


def _embed_batch(client: httpx.Client, batch: list[str]) -> list[list[float]]:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        response = client.post(
            HF_EMBEDDING_URL,
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={"inputs": batch, "normalize": True, "truncate": True},
        )
        if response.status_code in RETRY_STATUS and attempt < MAX_ATTEMPTS:
            time.sleep(2 ** attempt)
            continue
        response.raise_for_status()
        break

    vectors = response.json()
    if not (isinstance(vectors, list) and len(vectors) == len(batch) and all(len(v) == MODEL_VECTOR_SIZE for v in vectors)):
        raise ValueError(f"Unexpected embedding response shape; expected {len(batch)}x{MODEL_VECTOR_SIZE}")
    return vectors


# Union -> OR operator
# Allows for individual string or lists as input
# Expecting a single vector or a list of vectors (lists) as the return datatype
def embed_chunks(text: Union[str, list[str]]) -> Union[list[float], list[list[float]]]:
    if not HF_TOKEN:
        raise RuntimeError("HUGGING_FACE_ACCESS_TOKEN is not set; cannot call the HuggingFace Inference API")

    texts = [text] if isinstance(text, str) else text
    try:
        with httpx.Client(timeout=30) as client:
            vectors = [
                vector
                for i in range(0, len(texts), BATCH_SIZE)
                for vector in _embed_batch(client, texts[i:i + BATCH_SIZE])
            ]
    except Exception as e:
        logger.error(f"[Text Embedding] Error: {e}")
        raise

    return vectors[0] if isinstance(text, str) else vectors

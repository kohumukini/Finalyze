from sentence_transformers import SentenceTransformer
from typing import Union

from ..core.logger import get_logger
from ..core.config import EMBEDDING_MODEL

logger = get_logger(__name__)

model = None


def _get_model() -> SentenceTransformer:
    global model
    if model is None:
        model = SentenceTransformer(EMBEDDING_MODEL)
    return model

# Union -> OR operator
# Allows for individual string or lists as input
# Expecting a single vector or a list of vectors (lists) as the return datatype
def embed_chunks(text: Union[str, list[str]]) -> Union[list[float], list[list[float]]]: 
    try: 
        embeddings = _get_model().encode(
            text, 
            batch_size=32,
            show_progress_bar=False
        )
        
        return embeddings.tolist()
    except Exception as e: 
        logger.error(f"[Text Embedding] Error: {e}")
        raise
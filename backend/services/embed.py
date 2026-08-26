from sentence_transformers import SentenceTransformer
from typing import Union
from sqlalchemy.orm import Session

from ..core.logger import get_logger
from ..core.config import EMBEDDING_MODEL

logger = get_logger(__name__)
try:
    model = SentenceTransformer(EMBEDDING_MODEL)
except Exception as e:
    logger.error(f"[Embedding Model Activation] Error: {e}")
    raise

# Union -> OR operator
# Allows for individual string or lists as input
# Expecting a single vector or a list of vectors (lists) as the return datatype
def embed_chunks(text: Union[str, list[str]]) -> Union[list[float], list[list[float]]]: 
    try: 
        embeddings = model.encode(
            text, 
            batch_size=32,
            show_progress_bar=False
        )
        
        return embeddings
    except Exception as e: 
        logger.error(f"[Text Embedding] Error: {e}")
        raise
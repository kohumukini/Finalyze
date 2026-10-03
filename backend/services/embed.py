from typing import Union

from ..core.logger import get_logger
from ..core.config import EMBEDDING_MODEL, HUGGING_FACE_TOKEN

from huggingface_hub import InferenceClient

logger = get_logger(__name__)

class HFInferenceEmbeddings: 
    def __init__(self): 
        self.client = InferenceClient(
            token=HUGGING_FACE_TOKEN, 
            model=EMBEDDING_MODEL
        )
        
    def encode(self, texts: list[str], batch_size: int, **kwargs):
        if isinstance(texts, str):
            texts = [texts]
            
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.feature_extraction(batch, **kwargs)
            
            if hasattr(response, "tolist"):
                response = response.tolist()
            
            all_embeddings.extend(response)
            
        return all_embeddings
        
embedding_service = HFInferenceEmbeddings()

# Union -> OR operator
# Allows for individual string or lists as input
# Expecting a single vector or a list of vectors (lists) as the return datatype
def embed_chunks(text: Union[str, list[str]]) -> Union[list[float], list[list[float]]]: 
    try: 
        embeddings = embedding_service.encode(
            text, 
            batch_size=32
        )
        
        return embeddings
    except Exception as e: 
        logger.error(f"[Text Embedding] Error: {e}")
        raise
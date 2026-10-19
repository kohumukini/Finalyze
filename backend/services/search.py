from ..core.database import Chunks
from ..core.logger import get_logger
from ..core.schema import Source
from .embed import embed_chunks

from sqlalchemy import select
from sqlalchemy.orm import Session

logger = get_logger(__name__)

def retrieve_sources(user_prompt: str, db: Session, top_k: int = 4) -> list[Source]:
    query_embedding = embed_chunks([user_prompt])[0]
    statement = (
        select(Chunks)
        .order_by(Chunks.embedding.cosine_distance(query_embedding))
        .limit(top_k)
    )
    chunks = db.execute(statement).scalars().all()
    
    logger.info(f"[Text Retrieval] Retrieved {len(chunks)} chunks")
    
    # With the use of model_config, pydantic will coherce the data to fit the model
    return [Source.model_validate(c) for c in chunks]

# Grab the document names stored within the database
# Helps contextualize the llm gatekeeper in it's decision
def list_document_names(db: Session) -> list[str]: 
    return list(db.scalars(select(Chunks.document_name).distinct()))
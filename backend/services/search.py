from ..core.database import Chunks
from ..core.logger import get_logger
from ..core.schema import Source
from ..core.config import MAX_DISTANCE
from .embed import embed_chunks

from sqlalchemy import select
from sqlalchemy.orm import Session

logger = get_logger(__name__)

def retrieve_sources(prompts: list[str], db: Session, top_k: int = 4) -> list[Source]:
    seen_ids = set()
    unique_chunks_with_distance = []    
    query_embeddings = embed_chunks(prompts)
    
    for query in query_embeddings: 
        distance_expr = Chunks.embedding.cosine_distance(query)
    
        statement = (
            select(Chunks, distance_expr.label("distance"))
            .order_by(distance_expr)
            .limit(top_k)
        )
        
        results = db.execute(statement).all()
        
        for chunk, distance in results: 
            if chunk.chunk_id not in seen_ids and distance <= MAX_DISTANCE:
                seen_ids.add(chunk.chunk_id)
                unique_chunks_with_distance.append((distance, chunk))
                
                logger.info(f"{chunk.chunk_id} - {chunk.document_name}: Distance = {distance}")
    
    unique_chunks_with_distance.sort(key=lambda x: x[0])
    sorted_chunks = [chunk for distance, chunk in unique_chunks_with_distance]
    logger.info(f"[Text Retrieval] Retrieved {len(sorted_chunks)} chunks")
    
    # With the use of model_config, pydantic will coherce the data to fit the model
    return [Source.model_validate(c) for c in sorted_chunks[:8]]

# Grab the document names stored within the database
# Helps contextualize the llm gatekeeper in it's decision
def list_document_names(db: Session) -> list[str]: 
    return list(db.scalars(select(Chunks.document_name).distinct()))
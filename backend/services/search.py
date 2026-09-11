from ..core.database import Chunks
from ..core.logger import get_logger
from .embed import embed_chunks

from sqlalchemy import select
from sqlalchemy.orm import Session

logger = get_logger(__name__)

def retrieve_text(user_prompt: str, db: Session, top_k: int = 4) -> list[str]:
    query_embedding = embed_chunks(user_prompt)
    statement = (
        select(Chunks)
        .order_by(Chunks.embedding.cosine_distance(query_embedding))
        .limit(top_k)
    )

    logger.info("[Text Retrieval] Executing")
    chunks = db.execute(statement).scalars().all()
    return [chunk.content for chunk in chunks]
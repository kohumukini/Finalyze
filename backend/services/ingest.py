import os
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.database import Chunks, Documents, SessionLocal, init_db
from ..core.logger import configure_logging, get_logger
from .embed import embed_chunks
from .chunk import chunk_doc

logger = get_logger(__name__)
DOCS_DIR = Path(__file__).resolve().parents[2] / "docs"

def load_documents(): 
    documents = []
    for filename in sorted(os.listdir(DOCS_DIR)):
        if filename.endswith(".txt"): 
            filepath = DOCS_DIR / filename
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            documents.append({
                "filename": filename, 
                "text": text
            })
            
    logger.info("Loaded %d document(s)", len(documents))
    return documents

def ingest_documents(db: Session) -> int:
    """Replace the database copy of local text documents and their embeddings."""
    ingested_chunks = 0
    for document_data in load_documents():
        chunks = [c for c in chunk_doc(document_data["text"]) if c]
        document = db.execute(
            select(Documents).where(Documents.metadata_["name"].astext == document_data["filename"])
        ).scalar_one_or_none()

        if document is None:
            document = Documents(
                content=document_data["text"],
                metadata_={"name": document_data["filename"]},
            )
            db.add(document)
            db.flush()
        else:
            document.content = document_data["text"]
            document.chunks.clear()

        embeddings = embed_chunks(chunks)
        document.chunks.extend(
            Chunks(content=content, embedding=embedding, metadata_={"source": document_data["filename"]})
            for content, embedding in zip(chunks, embeddings)
        )
        ingested_chunks += len(chunks)

    db.commit()
    return ingested_chunks

if __name__ == "__main__":
    configure_logging()
    init_db()
    with SessionLocal() as db:
        logger.info("Ingested %d chunk(s)", ingest_documents(db))

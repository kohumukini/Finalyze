import os
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.database import Chunks, Documents
from .embed import embed_chunks
from .chunk import chunk_doc

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
            
    print(f"Loaded {len(documents)} document(s)")
    return documents

def load_chunks(): 
    docs = load_documents()
    
    chunked_docs = []
    
    for doc in docs: 
        chunked_docs.append({
            "filename": doc["filename"],
            "content": chunk_doc(doc["text"])
        })
    return chunked_docs

def ingest_documents(db: Session) -> int:
    """Replace the database copy of local text documents and their embeddings."""
    ingested_chunks = 0
    for document_data in load_documents():
        chunks = chunk_doc(document_data["text"])
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
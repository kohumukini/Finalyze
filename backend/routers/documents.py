from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.database import Documents, get_db_session
from ..core.logger import get_logger
from ..core.schema import DocumentItem

logger = get_logger(__name__)
router = APIRouter(prefix="/docs", tags=["documents"])


@router.get("", response_model=list[DocumentItem])
def list_documents(db: Session = Depends(get_db_session)):
    try:
        stmt = select(Documents)
        result = db.execute(stmt).scalars().all()
        documents = [
            DocumentItem(
                document_id=document.document_id,
                document_name=document.document_name,
                timestamp=document.timestamp,
                content=document.content,
            )
            for document in result
        ]
        logger.info("Fetched %d documents from the database", len(documents))
        return documents
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Error fetching documents: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch documents.") from exc


@router.get("/{document_name}", response_model=DocumentItem)
def get_document_by_name(document_name: str, db: Session = Depends(get_db_session)):
    try:
        statement = select(Documents).where(Documents.document_name == document_name)
        document = db.execute(statement).unique().scalar_one_or_none()

        if document is None:
            logger.warning("Document '%s' not found", document_name)
            raise HTTPException(status_code=404, detail=f"Document '{document_name}' not found.")

        logger.info("Retrieved document '%s' with id %s", document_name, document.document_id)
        return DocumentItem(
            document_id=document.document_id,
            document_name=document.document_name,
            timestamp=document.timestamp,
            content=document.content,
        )
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Error fetching document '%s': %s", document_name, exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch document.") from exc

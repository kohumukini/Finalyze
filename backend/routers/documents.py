from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.database import Documents, get_db_session
from ..core.schema import DocumentCreateRequest, DocumentItem

router = APIRouter(prefix="/docs", tags=["documents"])


@router.get("", response_model=list[DocumentItem])
def list_documents(db: Session = Depends(get_db_session)):
    try:
        stmt = select(Documents)
        result = db.execute(stmt).scalars().all()
        return [
            DocumentItem(
                document_id=document.document_id,
                document_name=document.metadata_.get("name", f"document_{document.document_id}"),
                timestamp=document.timestamp,
                content=document.content,
                metadata=document.metadata_,
            )
            for document in result
        ]
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to fetch documents: {exc}") from exc


@router.put("", response_model=DocumentItem, status_code=status.HTTP_201_CREATED)
def add_document(payload: DocumentCreateRequest, db: Session = Depends(get_db_session)):
    try:
        document = Documents(
            content=payload.content,
            metadata_={**payload.metadata, "name": payload.document_name},
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        return DocumentItem(
            document_id=document.document_id,
            document_name=document.metadata_.get("name", payload.document_name),
            timestamp=document.timestamp,
            content=document.content,
            metadata=document.metadata_,
        )
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create document: {exc}") from exc


@router.get("/{document_name}", response_model=DocumentItem)
def get_document_by_name(document_name: str, db: Session = Depends(get_db_session)):
    try:
        result = db.execute(select(Documents)).scalars().all()
        document = next(
            (item for item in result if item.metadata_.get("name") == document_name),
            None,
        )

        if document is None:
            raise HTTPException(status_code=404, detail=f"Document '{document_name}' not found.")

        return DocumentItem(
            document_id=document.document_id,
            document_name=document.metadata_.get("name", document_name),
            timestamp=document.timestamp,
            content=document.content,
            metadata=document.metadata_,
        )
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to fetch document: {exc}") from exc

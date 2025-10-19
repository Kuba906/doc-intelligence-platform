from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.database import Document, DocumentStatus
from app.models.schemas import DocumentDetail, DocumentListResponse, DocumentListItem

router = APIRouter()


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    tenant_id: str = Query(default="demo"),
    status_filter: Optional[DocumentStatus] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List documents with pagination and filtering"""
    query = db.query(Document).filter(Document.tenant_id == tenant_id)

    if status_filter:
        query = query.filter(Document.status == status_filter)

    total = query.count()
    documents = query.order_by(Document.uploaded_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    return DocumentListResponse(
        documents=[DocumentListItem.from_orm(doc) for doc in documents],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Get document details by ID"""
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    return DocumentDetail.from_orm(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Delete a document"""
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    # TODO: Delete from blob storage as well

    db.delete(document)
    db.commit()

    return None


@router.post("/{document_id}/reprocess", status_code=status.HTTP_202_ACCEPTED)
async def reprocess_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Trigger reprocessing of a document"""
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    # Reset status
    document.status = DocumentStatus.UPLOADED
    document.retry_count += 1
    db.commit()

    # Trigger background job
    from app.workers.process_documents import process_document_task
    process_document_task.delay(document_id)

    return {"message": "Reprocessing triggered", "document_id": document_id}

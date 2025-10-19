from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from app.core.deps import PaginationParams, TenantParams, get_document_service
from app.models.database import DocumentStatus
from app.models.schemas import DocumentDetail, DocumentListResponse, DocumentListItem
from app.services.document_service import DocumentService

router = APIRouter()


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    tenant: TenantParams = Depends(),
    pagination: PaginationParams = Depends(),
    status_filter: Optional[DocumentStatus] = None,
    service: DocumentService = Depends(get_document_service)
):
    """List documents with pagination and filtering"""
    documents, total = service.list_documents(
        tenant_id=tenant.tenant_id,
        status_filter=status_filter,
        skip=pagination.skip,
        limit=pagination.page_size
    )

    return DocumentListResponse(
        documents=[DocumentListItem.from_orm(doc) for doc in documents],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service)
):
    """Get document details by ID"""
    document = service.get_by_id(document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    return DocumentDetail.from_orm(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service)
):
    """Delete a document"""
    deleted = service.delete_document(document_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    return None


@router.post("/{document_id}/reprocess", status_code=status.HTTP_202_ACCEPTED)
async def reprocess_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service)
):
    """Trigger reprocessing of a document"""
    document = service.reprocess_document(document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    # Trigger background job
    from app.workers.process_documents import process_document_task
    process_document_task.delay(document_id)

    return {"message": "Reprocessing triggered", "document_id": document_id}

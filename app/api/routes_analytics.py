from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.database import Document, DocumentStatus, DocumentType
from app.models.schemas import DocumentStats

router = APIRouter()


@router.get("/stats", response_model=DocumentStats)
async def get_stats(
    tenant_id: str = Query(default="demo"),
    db: Session = Depends(get_db)
):
    """Get document processing statistics"""
    # Total documents
    total = db.query(func.count(Document.id)) \
        .filter(Document.tenant_id == tenant_id) \
        .scalar()

    # By status
    by_status = {}
    status_counts = db.query(Document.status, func.count(Document.id)) \
        .filter(Document.tenant_id == tenant_id) \
        .group_by(Document.status) \
        .all()
    for status, count in status_counts:
        by_status[status.value] = count

    # By type
    by_type = {}
    type_counts = db.query(Document.document_type, func.count(Document.id)) \
        .filter(Document.tenant_id == tenant_id) \
        .filter(Document.document_type.isnot(None)) \
        .group_by(Document.document_type) \
        .all()
    for doc_type, count in type_counts:
        if doc_type:
            by_type[doc_type.value] = count

    # Average confidence
    avg_confidence = db.query(func.avg(Document.confidence_score)) \
        .filter(Document.tenant_id == tenant_id) \
        .filter(Document.confidence_score.isnot(None)) \
        .scalar()

    # Average processing time
    avg_time = db.query(func.avg(Document.processing_time_seconds)) \
        .filter(Document.tenant_id == tenant_id) \
        .filter(Document.processing_time_seconds.isnot(None)) \
        .scalar()

    # Total storage
    total_storage_bytes = db.query(func.sum(Document.file_size_bytes)) \
        .filter(Document.tenant_id == tenant_id) \
        .scalar() or 0
    total_storage_mb = total_storage_bytes / (1024 * 1024)

    return DocumentStats(
        total_documents=total,
        by_status=by_status,
        by_type=by_type,
        avg_confidence=float(avg_confidence) if avg_confidence else None,
        avg_processing_time=float(avg_time) if avg_time else None,
        total_storage_mb=round(total_storage_mb, 2)
    )

"""
Analytics service layer - handles statistics and metrics.
Encapsulates complex database queries for analytics.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.database import Document, DocumentStatus, DocumentType


class AnalyticsService:
    """Service for analytics and statistics operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_total_documents(self, tenant_id: str) -> int:
        """Get total document count for a tenant"""
        return self.db.query(func.count(Document.id)) \
            .filter(Document.tenant_id == tenant_id) \
            .scalar() or 0

    def get_documents_by_status(self, tenant_id: str) -> dict[str, int]:
        """Get document counts grouped by status"""
        by_status = {}
        status_counts = self.db.query(Document.status, func.count(Document.id)) \
            .filter(Document.tenant_id == tenant_id) \
            .group_by(Document.status) \
            .all()

        for status, count in status_counts:
            by_status[status.value] = count

        return by_status

    def get_documents_by_type(self, tenant_id: str) -> dict[str, int]:
        """Get document counts grouped by type"""
        by_type = {}
        type_counts = self.db.query(Document.document_type, func.count(Document.id)) \
            .filter(Document.tenant_id == tenant_id) \
            .filter(Document.document_type.isnot(None)) \
            .group_by(Document.document_type) \
            .all()

        for doc_type, count in type_counts:
            if doc_type:
                by_type[doc_type.value] = count

        return by_type

    def get_average_confidence(self, tenant_id: str) -> float | None:
        """Get average confidence score across all documents"""
        avg_confidence = self.db.query(func.avg(Document.confidence_score)) \
            .filter(Document.tenant_id == tenant_id) \
            .filter(Document.confidence_score.isnot(None)) \
            .scalar()

        return float(avg_confidence) if avg_confidence else None

    def get_average_processing_time(self, tenant_id: str) -> float | None:
        """Get average processing time in seconds"""
        avg_time = self.db.query(func.avg(Document.processing_time_seconds)) \
            .filter(Document.tenant_id == tenant_id) \
            .filter(Document.processing_time_seconds.isnot(None)) \
            .scalar()

        return float(avg_time) if avg_time else None

    def get_total_storage(self, tenant_id: str) -> float:
        """Get total storage used in MB"""
        total_storage_bytes = self.db.query(func.sum(Document.file_size_bytes)) \
            .filter(Document.tenant_id == tenant_id) \
            .scalar() or 0

        return round(total_storage_bytes / (1024 * 1024), 2)

    def get_comprehensive_stats(self, tenant_id: str) -> dict:
        """
        Get all statistics in a single call.
        Returns a comprehensive dictionary of all metrics.
        """
        return {
            "total_documents": self.get_total_documents(tenant_id),
            "by_status": self.get_documents_by_status(tenant_id),
            "by_type": self.get_documents_by_type(tenant_id),
            "avg_confidence": self.get_average_confidence(tenant_id),
            "avg_processing_time": self.get_average_processing_time(tenant_id),
            "total_storage_mb": self.get_total_storage(tenant_id)
        }

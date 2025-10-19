"""
Document service layer - handles document business logic.
Keeps routes clean by encapsulating database operations.
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.models.database import Document, DocumentStatus


class DocumentService:
    """Service for document-related operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, document_id: str) -> Optional[Document]:
        """Get a document by ID"""
        return self.db.query(Document).filter(Document.id == document_id).first()

    def list_documents(
        self,
        tenant_id: str,
        status_filter: Optional[DocumentStatus] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list[Document], int]:
        """
        List documents with filtering and pagination.
        Returns (documents, total_count)
        """
        query = self.db.query(Document).filter(Document.tenant_id == tenant_id)

        if status_filter:
            query = query.filter(Document.status == status_filter)

        total = query.count()
        documents = query.order_by(Document.uploaded_at.desc()) \
            .offset(skip) \
            .limit(limit) \
            .all()

        return documents, total

    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document.
        Returns True if deleted, False if not found.
        """
        document = self.get_by_id(document_id)
        if not document:
            return False

        # TODO: Delete from blob storage as well
        self.db.delete(document)
        self.db.commit()
        return True

    def reprocess_document(self, document_id: str) -> Optional[Document]:
        """
        Reset document status and trigger reprocessing.
        Returns the document if found, None otherwise.
        """
        document = self.get_by_id(document_id)
        if not document:
            return None

        # Reset status for reprocessing
        document.status = DocumentStatus.UPLOADED
        document.retry_count += 1
        self.db.commit()
        self.db.refresh(document)

        return document

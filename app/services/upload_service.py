"""
Upload service layer - handles file upload business logic.
Encapsulates validation, storage, and database operations.
"""
from typing import BinaryIO
from sqlalchemy.orm import Session
import structlog

from app.core.config import settings
from app.models.database import Document, DocumentStatus
from app.services.storage_service import StorageService

logger = structlog.get_logger()


class FileValidationError(Exception):
    """Custom exception for file validation errors"""
    pass


class UploadService:
    """Service for document upload operations"""

    def __init__(self, db: Session):
        self.db = db
        self.storage_service = StorageService()

    def validate_file_extension(self, filename: str) -> str:
        """
        Validate file extension.
        Returns the extension if valid, raises FileValidationError otherwise.
        """
        file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''

        if file_ext not in settings.ALLOWED_FILE_EXTENSIONS:
            raise FileValidationError(
                f"File type {file_ext} not allowed. Allowed types: {settings.ALLOWED_FILE_EXTENSIONS}"
            )

        return file_ext

    def validate_file_size(self, file_size: int) -> None:
        """
        Validate file size.
        Raises FileValidationError if file is too large.
        """
        max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024

        if file_size > max_size_bytes:
            raise FileValidationError(
                f"File size {file_size / (1024*1024):.2f}MB exceeds maximum {settings.MAX_FILE_SIZE_MB}MB"
            )

    async def upload_document(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str,
        file_size: int,
        tenant_id: str
    ) -> Document:
        """
        Upload a document to storage and create database record.
        Handles validation, storage upload, and database creation.
        """
        # Validate
        self.validate_file_extension(filename)
        self.validate_file_size(file_size)

        # Upload to blob storage
        blob_uri = await self.storage_service.upload_file(
            file=file,
            filename=filename,
            content_type=content_type
        )

        # Create database record
        document = Document(
            tenant_id=tenant_id,
            filename=filename,
            content_type=content_type,
            file_size_bytes=file_size,
            blob_uri=blob_uri,
            status=DocumentStatus.UPLOADED
        )

        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        logger.info(
            "document_uploaded",
            document_id=document.id,
            filename=filename,
            tenant_id=tenant_id,
            file_size=file_size
        )

        return document

    async def batch_upload_documents(
        self,
        files: list[tuple[BinaryIO, str, str, int]],  # (file, filename, content_type, size)
        tenant_id: str
    ) -> tuple[list[Document], list[dict]]:
        """
        Upload multiple documents.
        Returns (successful_documents, errors)
        """
        results = []
        errors = []

        for file, filename, content_type, file_size in files:
            try:
                document = await self.upload_document(
                    file=file,
                    filename=filename,
                    content_type=content_type,
                    file_size=file_size,
                    tenant_id=tenant_id
                )
                results.append(document)
            except FileValidationError as e:
                errors.append({
                    "filename": filename,
                    "error": str(e)
                })
            except Exception as e:
                logger.error("batch_upload_failed", error=str(e), filename=filename)
                errors.append({
                    "filename": filename,
                    "error": str(e)
                })

        return results, errors

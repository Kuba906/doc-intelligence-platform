from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.core.config import settings
from app.models.database import Document, DocumentStatus
from app.models.schemas import DocumentUploadResponse
from app.services.storage_service import StorageService
from app.workers.process_documents import process_document_task

logger = structlog.get_logger()
router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    tenant_id: str = Form(default=settings.DEFAULT_TENANT_ID),
    db: Session = Depends(get_db)
):
    """
    Upload a document for processing.

    - **file**: Document file (PDF, image, DOCX)
    - **tenant_id**: Tenant identifier (defaults to 'demo')
    """
    # Validate file extension
    file_ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if file_ext not in settings.ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed types: {settings.ALLOWED_FILE_EXTENSIONS}"
        )

    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size {file_size / (1024*1024):.2f}MB exceeds maximum {settings.MAX_FILE_SIZE_MB}MB"
        )

    try:
        # Upload to blob storage
        storage_service = StorageService()
        blob_uri = await storage_service.upload_file(
            file=file.file,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream"
        )

        # Create database record
        document = Document(
            tenant_id=tenant_id,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            file_size_bytes=file_size,
            blob_uri=blob_uri,
            status=DocumentStatus.UPLOADED
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        # Trigger background processing
        process_document_task.delay(document.id)

        logger.info(
            "document_uploaded",
            document_id=document.id,
            filename=file.filename,
            tenant_id=tenant_id,
            file_size=file_size
        )

        return DocumentUploadResponse(
            id=document.id,
            filename=document.filename,
            status=document.status,
            uploaded_at=document.uploaded_at
        )

    except Exception as e:
        logger.error("upload_failed", error=str(e), filename=file.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.post("/batch-upload")
async def batch_upload(
    files: list[UploadFile] = File(...),
    tenant_id: str = Form(default=settings.DEFAULT_TENANT_ID),
    db: Session = Depends(get_db)
):
    """
    Upload multiple documents at once.
    """
    results = []
    errors = []

    for file in files:
        try:
            result = await upload_document(file=file, tenant_id=tenant_id, db=db)
            results.append(result)
        except HTTPException as e:
            errors.append({
                "filename": file.filename,
                "error": e.detail
            })
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })

    return {
        "uploaded": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
import structlog

from app.core.config import settings
from app.core.deps import get_upload_service
from app.models.schemas import DocumentUploadResponse
from app.services.upload_service import UploadService, FileValidationError
from app.workers.process_documents import process_document_task

logger = structlog.get_logger()
router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    tenant_id: str = Form(default=settings.DEFAULT_TENANT_ID),
    service: UploadService = Depends(get_upload_service)
):
    """
    Upload a document for processing.

    - **file**: Document file (PDF, image, DOCX)
    - **tenant_id**: Tenant identifier (defaults to 'demo')
    """
    # Get file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    try:
        # Upload document via service (handles validation + storage + DB)
        document = await service.upload_document(
            file=file.file,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            file_size=file_size,
            tenant_id=tenant_id
        )

        # Trigger background processing
        process_document_task.delay(document.id)

        return DocumentUploadResponse(
            id=document.id,
            filename=document.filename,
            status=document.status,
            uploaded_at=document.uploaded_at
        )

    except FileValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
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
    service: UploadService = Depends(get_upload_service)
):
    """
    Upload multiple documents at once.
    """
    # Prepare file data
    file_data = []
    for file in files:
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        file_data.append((
            file.file,
            file.filename,
            file.content_type or "application/octet-stream",
            file_size
        ))

    # Upload via service
    documents, errors = await service.batch_upload_documents(file_data, tenant_id)

    # Trigger background processing for successful uploads
    for document in documents:
        process_document_task.delay(document.id)

    # Convert documents to response format
    results = [
        DocumentUploadResponse(
            id=doc.id,
            filename=doc.filename,
            status=doc.status,
            uploaded_at=doc.uploaded_at
        )
        for doc in documents
    ]

    return {
        "uploaded": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }

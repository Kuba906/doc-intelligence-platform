from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.database import DocumentStatus, DocumentType


# Document Schemas
class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    status: DocumentStatus
    uploaded_at: datetime

    class Config:
        from_attributes = True


class DocumentDetail(BaseModel):
    id: str
    tenant_id: str
    filename: str
    content_type: str
    file_size_bytes: int
    status: DocumentStatus
    document_type: Optional[DocumentType]
    extracted_fields: Optional[Dict[str, Any]]
    entities: Optional[List[Dict[str, Any]]]
    summary: Optional[str]
    confidence_score: Optional[float]
    processing_time_seconds: Optional[float]
    error_message: Optional[str]
    uploaded_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


class DocumentListItem(BaseModel):
    id: str
    filename: str
    status: DocumentStatus
    document_type: Optional[DocumentType]
    confidence_score: Optional[float]
    uploaded_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentListItem]
    total: int
    page: int
    page_size: int


# Analytics Schemas
class DocumentStats(BaseModel):
    total_documents: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    avg_confidence: Optional[float]
    avg_processing_time: Optional[float]
    total_storage_mb: float


class TenantStats(BaseModel):
    tenant_id: str
    documents_processed_this_month: int
    max_documents_per_month: int
    storage_used_mb: float
    max_storage_mb: int
    is_within_limits: bool


# Processing Schemas
class ProcessingResult(BaseModel):
    document_id: str
    status: DocumentStatus
    document_type: Optional[DocumentType]
    extracted_fields: Dict[str, Any]
    entities: List[Dict[str, Any]]
    summary: Optional[str]
    confidence_score: float
    processing_time_seconds: float


# Error Schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    request_id: Optional[str] = None

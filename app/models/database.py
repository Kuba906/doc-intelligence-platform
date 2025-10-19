from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, JSON, Text, Index
from sqlalchemy.sql import func
from app.core.database import Base
import enum
from datetime import datetime
import uuid


class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentType(str, enum.Enum):
    INVOICE = "invoice"
    RECEIPT = "receipt"
    CONTRACT = "contract"
    BUSINESS_CARD = "business_card"
    IDENTITY = "identity"
    BANK_STATEMENT = "bank_statement"
    TAX_FORM = "tax_form"
    OTHER = "other"


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)

    # File metadata
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    blob_uri = Column(String, nullable=False)

    # Processing status
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED, index=True)
    document_type = Column(Enum(DocumentType), nullable=True)

    # Extracted data (JSON)
    extracted_fields = Column(JSON, nullable=True)
    entities = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)

    # Quality metrics
    confidence_score = Column(Float, nullable=True)
    processing_time_seconds = Column(Float, nullable=True)

    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes for common queries
    __table_args__ = (
        Index('idx_tenant_status', 'tenant_id', 'status'),
        Index('idx_tenant_type', 'tenant_id', 'document_type'),
        Index('idx_uploaded_at', 'uploaded_at'),
    )


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)

    # Usage tracking
    documents_processed_total = Column(Integer, default=0)
    documents_processed_this_month = Column(Integer, default=0)
    storage_used_bytes = Column(Integer, default=0)

    # Plan & limits
    plan = Column(String, default="free")
    max_documents_per_month = Column(Integer, default=100)
    max_storage_mb = Column(Integer, default=1000)

    # Status
    is_active = Column(Integer, default=1)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

"""
Dependency injection providers for FastAPI routes.
Similar to .NET Core's dependency injection system.
"""
from typing import Annotated
from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings


# ===== Common Query Parameters =====

class PaginationParams:
    """Reusable pagination parameters"""
    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="Page number"),
        page_size: int = Query(default=20, ge=1, le=100, description="Items per page")
    ):
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size


class TenantParams:
    """Reusable tenant identification"""
    def __init__(
        self,
        tenant_id: str = Query(default=settings.DEFAULT_TENANT_ID, description="Tenant identifier")
    ):
        self.tenant_id = tenant_id


# ===== Service Dependencies =====

def get_document_service(db: Session = Depends(get_db)):
    """Provide DocumentService instance (Scoped)"""
    from app.services.document_service import DocumentService
    return DocumentService(db)


def get_upload_service(db: Session = Depends(get_db)):
    """Provide UploadService instance (Scoped)"""
    from app.services.upload_service import UploadService
    return UploadService(db)


def get_analytics_service(db: Session = Depends(get_db)):
    """Provide AnalyticsService instance (Scoped)"""
    from app.services.analytics_service import AnalyticsService
    return AnalyticsService(db)


# ===== Type Annotations for Cleaner Routes =====

# Use these type hints to make routes even cleaner
DbSession = Annotated[Session, Depends(get_db)]
Pagination = Annotated[PaginationParams, Depends()]
Tenant = Annotated[TenantParams, Depends()]

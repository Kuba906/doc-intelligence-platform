from fastapi import APIRouter, Depends

from app.core.deps import TenantParams, get_analytics_service
from app.models.schemas import DocumentStats
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/stats", response_model=DocumentStats)
async def get_stats(
    tenant: TenantParams = Depends(),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get document processing statistics"""
    stats = service.get_comprehensive_stats(tenant.tenant_id)

    return DocumentStats(**stats)

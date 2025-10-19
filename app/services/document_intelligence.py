from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class DocumentIntelligenceService:
    def __init__(self):
        if not settings.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT:
            logger.warning("Azure Document Intelligence not configured, using mock")
            self.client = None
        else:
            self.client = DocumentAnalysisClient(
                endpoint=settings.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT,
                credential=AzureKeyCredential(settings.AZURE_DOCUMENT_INTELLIGENCE_KEY)
            )

    async def analyze_document(self, blob_uri: str, document_type_hint: str = None):
        """
        Analyze document using Azure Document Intelligence

        Returns: Dictionary with extracted fields and confidence
        """
        if not self.client:
            # Mock response for development
            logger.info("using_mock_document_intelligence")
            return {
                "fields": {
                    "vendor_name": {"value": "Acme Corp", "confidence": 0.98},
                    "total": {"value": "1234.56", "confidence": 0.95},
                    "date": {"value": "2024-10-18", "confidence": 0.92}
                },
                "document_type": "invoice",
                "confidence": 0.95
            }

        try:
            # Choose model based on document type hint
            model_id = self._get_model_id(document_type_hint)

            logger.info("analyzing_document", blob_uri=blob_uri, model=model_id)

            # Analyze document from URL
            poller = await self.client.begin_analyze_document_from_url(
                model_id=model_id,
                document_url=blob_uri
            )

            result = await poller.result()

            # Extract fields
            fields = {}
            for doc in result.documents:
                for field_name, field_value in doc.fields.items():
                    fields[field_name] = {
                        "value": field_value.content if hasattr(field_value, 'content') else str(field_value.value),
                        "confidence": field_value.confidence or 0.0
                    }

            # Calculate overall confidence
            confidences = [f["confidence"] for f in fields.values() if f["confidence"] > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            return {
                "fields": fields,
                "document_type": self._map_model_to_type(model_id),
                "confidence": avg_confidence
            }

        except Exception as e:
            logger.error("document_analysis_failed", error=str(e), blob_uri=blob_uri)
            raise

    def _get_model_id(self, document_type_hint: str = None) -> str:
        """Map document type to Azure prebuilt model"""
        type_to_model = {
            "invoice": "prebuilt-invoice",
            "receipt": "prebuilt-receipt",
            "business_card": "prebuilt-businessCard",
            "identity": "prebuilt-idDocument",
        }
        return type_to_model.get(document_type_hint, "prebuilt-document")

    def _map_model_to_type(self, model_id: str) -> str:
        """Map model ID back to document type"""
        model_to_type = {
            "prebuilt-invoice": "invoice",
            "prebuilt-receipt": "receipt",
            "prebuilt-businessCard": "business_card",
            "prebuilt-idDocument": "identity",
        }
        return model_to_type.get(model_id, "other")

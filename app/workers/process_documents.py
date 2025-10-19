from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.database import Document, DocumentStatus, DocumentType
from app.services.document_intelligence import DocumentIntelligenceService
from app.services.openai_service import OpenAIService
from app.services.ner_service import get_ner_service
import structlog
import time
from datetime import datetime

logger = structlog.get_logger()


@celery_app.task(name="process_document", bind=True, max_retries=3)
def process_document_task(self, document_id: str):
    """
    Background task to process a document:
    1. OCR with Azure Document Intelligence
    2. Classification with GPT-4o
    3. NER with transformers
    4. Summary generation
    """
    db = SessionLocal()

    try:
        logger.info("processing_document_started", document_id=document_id)
        start_time = time.time()

        # Get document from database
        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            logger.error("document_not_found", document_id=document_id)
            return {"status": "error", "message": "Document not found"}

        # Update status to processing
        document.status = DocumentStatus.PROCESSING
        db.commit()

        # 1. OCR & Field Extraction (Azure Document Intelligence)
        doc_intel_service = DocumentIntelligenceService()
        analysis_result = await doc_intel_service.analyze_document(
            blob_uri=document.blob_uri
        )

        extracted_fields = analysis_result["fields"]
        initial_confidence = analysis_result["confidence"]

        # 2. Document Classification (GPT-4o)
        openai_service = OpenAIService()
        document_type, class_confidence = await openai_service.classify_document(
            extracted_fields=extracted_fields
        )

        # Map to enum
        try:
            document.document_type = DocumentType(document_type)
        except ValueError:
            document.document_type = DocumentType.OTHER

        # 3. NER (Transformers with PyTorch)
        ner_service = get_ner_service()

        # Extract text from fields for NER
        text_for_ner = " ".join([
            str(field.get("value", ""))
            for field in extracted_fields.values()
        ])

        entities = await ner_service.extract_entities(text_for_ner)

        # 4. Summary Generation (GPT-4o)
        summary = await openai_service.generate_summary(
            extracted_fields=extracted_fields,
            document_type=document_type
        )

        # Calculate processing time
        processing_time = time.time() - start_time

        # Calculate average confidence
        avg_confidence = (initial_confidence + class_confidence) / 2

        # Update document in database
        document.extracted_fields = extracted_fields
        document.entities = entities
        document.summary = summary
        document.confidence_score = avg_confidence
        document.processing_time_seconds = processing_time
        document.status = DocumentStatus.COMPLETED
        document.processed_at = datetime.utcnow()
        document.error_message = None

        db.commit()

        logger.info(
            "processing_document_completed",
            document_id=document_id,
            document_type=document_type,
            confidence=avg_confidence,
            processing_time=processing_time,
            entities_count=len(entities)
        )

        return {
            "status": "completed",
            "document_id": document_id,
            "document_type": document_type,
            "confidence": avg_confidence,
            "processing_time": processing_time
        }

    except Exception as e:
        logger.error(
            "processing_document_failed",
            document_id=document_id,
            error=str(e),
            retry_count=self.request.retries
        )

        # Update document status to failed
        if document:
            document.status = DocumentStatus.FAILED
            document.error_message = str(e)
            db.commit()

        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

    finally:
        db.close()

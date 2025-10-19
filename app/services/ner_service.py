from transformers import pipeline
import structlog

logger = structlog.get_logger()


class NERService:
    def __init__(self):
        """Initialize NER pipeline with transformers (PyTorch backend)"""
        try:
            self.ner_pipeline = pipeline(
                "ner",
                model="dslim/bert-base-NER",
                aggregation_strategy="simple"
            )
            logger.info("ner_service_initialized")
        except Exception as e:
            logger.warning("ner_service_init_failed", error=str(e))
            self.ner_pipeline = None

    async def extract_entities(self, text: str) -> list[dict]:
        """
        Extract named entities from text using transformers (PyTorch)

        Returns: List of entities with type, text, and confidence
        """
        if not self.ner_pipeline:
            logger.warning("ner_pipeline_not_available")
            return []

        if not text or len(text) < 10:
            return []

        try:
            # Truncate text if too long (BERT max length)
            text = text[:512] if len(text) > 512 else text

            entities = self.ner_pipeline(text)

            # Format results
            formatted_entities = []
            for entity in entities:
                formatted_entities.append({
                    "text": entity["word"],
                    "type": entity["entity_group"],
                    "confidence": round(entity["score"], 3),
                    "start": entity.get("start"),
                    "end": entity.get("end")
                })

            logger.info("entities_extracted", count=len(formatted_entities))
            return formatted_entities

        except Exception as e:
            logger.error("ner_extraction_failed", error=str(e))
            return []

# Singleton instance
_ner_service = None


def get_ner_service() -> NERService:
    """Get or create NER service singleton"""
    global _ner_service
    if _ner_service is None:
        _ner_service = NERService()
    return _ner_service

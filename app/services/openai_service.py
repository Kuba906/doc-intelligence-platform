from openai import AzureOpenAI
from app.core.config import settings
import structlog
import json

logger = structlog.get_logger()


class OpenAIService:
    def __init__(self):
        if not settings.AZURE_OPENAI_ENDPOINT:
            logger.warning("Azure OpenAI not configured, using mock")
            self.client = None
        else:
            self.client = AzureOpenAI(
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION
            )

    async def classify_document(self, extracted_fields: dict) -> tuple[str, float]:
        """
        Classify document type using GPT-4o

        Returns: (document_type, confidence)
        """
        if not self.client:
            # Mock response
            return ("invoice", 0.92)

        prompt = f"""Classify this document into ONE of these types:
- invoice
- receipt
- contract
- business_card
- identity
- bank_statement
- tax_form
- other

Document fields:
{json.dumps(extracted_fields, indent=2)}

Respond with ONLY the document type (lowercase, one word)."""

        try:
            response = self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_CHAT,
                messages=[
                    {"role": "system", "content": "You are a document classification expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=10
            )

            classification = response.choices[0].message.content.strip().lower()

            # Map to our enum values
            type_mapping = {
                "business card": "business_card",
                "id": "identity",
                "bank statement": "bank_statement",
                "tax form": "tax_form"
            }
            classification = type_mapping.get(classification, classification)

            return (classification, 0.9)  # GPT confidence is implicit

        except Exception as e:
            logger.error("classification_failed", error=str(e))
            return ("other", 0.0)

    async def generate_summary(self, extracted_fields: dict, document_type: str) -> str:
        """Generate a summary of the document"""
        if not self.client:
            return f"Mock summary for {document_type} document"

        prompt = f"""Summarize this {document_type} document in 2-3 sentences.

Fields:
{json.dumps(extracted_fields, indent=2)}

Summary:"""

        try:
            response = self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_CHAT,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error("summary_generation_failed", error=str(e))
            return f"Summary generation failed: {str(e)}"

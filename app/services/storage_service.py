from azure.storage.blob import BlobServiceClient, ContentSettings
from app.core.config import settings
import uuid
import structlog

logger = structlog.get_logger()


class StorageService:
    def __init__(self):
        self.blob_service_client = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME
        self._ensure_container_exists()

    def _ensure_container_exists(self):
        """Create container if it doesn't exist"""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container()
                logger.info("container_created", container_name=self.container_name)
        except Exception as e:
            logger.error("container_check_failed", error=str(e))

    async def upload_file(self, file, filename: str, content_type: str) -> str:
        """
        Upload file to Azure Blob Storage

        Returns: Blob URI
        """
        try:
            # Generate unique blob name
            blob_name = f"{uuid.uuid4()}/{filename}"

            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            # Upload
            content_settings = ContentSettings(content_type=content_type)
            blob_client.upload_blob(
                file,
                overwrite=True,
                content_settings=content_settings
            )

            blob_uri = blob_client.url

            logger.info(
                "file_uploaded",
                filename=filename,
                blob_name=blob_name,
                size_bytes=file.tell()
            )

            return blob_uri

        except Exception as e:
            logger.error("upload_failed", filename=filename, error=str(e))
            raise

    async def download_file(self, blob_uri: str):
        """Download file from blob storage"""
        # TODO: Implement download
        pass

    async def delete_file(self, blob_uri: str):
        """Delete file from blob storage"""
        # TODO: Implement delete
        pass

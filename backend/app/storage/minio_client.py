"""
MinIO Client — Object storage interface.

Provides methods for interacting with MinIO (S3-compatible) storage:
- Uploading documents
- Downloading documents
- Listing objects
- Deleting objects
- Generating presigned URLs
"""

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class MinIOClient:
    """Async client for MinIO object storage.

    Wraps the MinIO Python SDK to provide document storage operations.
    All operations are scoped to the configured bucket.
    """

    def __init__(self) -> None:
        """Initialize the MinIO client.

        TODO: Initialize minio.Minio client with settings.
        """
        # TODO: Implement MinIO client initialization
        # self._client = Minio(
        #     endpoint=settings.minio.endpoint,
        #     access_key=settings.minio.access_key,
        #     secret_key=settings.minio.secret_key,
        #     secure=settings.minio.use_ssl,
        # )
        self._bucket = settings.minio.bucket_documents
        logger.info("MinIOClient initialized (stub)")

    async def upload_file(self, file_path: str, object_name: str) -> str:
        """Upload a file to MinIO.

        Args:
            file_path: Local path to the file to upload.
            object_name: Target object name in the bucket.

        Returns:
            str: The object URL in MinIO.

        Raises:
            NotImplementedError: Until storage is implemented.
        """
        # TODO: Implement file upload
        raise NotImplementedError("MinIO upload not yet implemented.")

    async def download_file(self, object_name: str, destination: str) -> None:
        """Download a file from MinIO.

        Args:
            object_name: Object name in the bucket.
            destination: Local path where the file will be saved.

        Raises:
            NotImplementedError: Until storage is implemented.
        """
        # TODO: Implement file download
        raise NotImplementedError("MinIO download not yet implemented.")

    async def get_presigned_url(self, object_name: str, expiry_hours: int = 24) -> str:
        """Generate a presigned URL for temporary access to an object.

        Args:
            object_name: Object name in the bucket.
            expiry_hours: URL validity duration in hours.

        Returns:
            str: Presigned URL for the object.

        Raises:
            NotImplementedError: Until storage is implemented.
        """
        # TODO: Implement presigned URL generation
        raise NotImplementedError("Presigned URL not yet implemented.")

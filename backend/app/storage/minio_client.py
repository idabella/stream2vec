"""
MinIO Client — S3-compatible object storage interface.

Wraps the MinIO Python SDK to provide:
- Bucket initialization on startup
- Connectivity health check
- File upload / download / presigned URL (stubs ready for Phase 2)

The client is initialized once at application startup (lifespan) and
exposed via FastAPI dependency injection.
"""

import logging
from io import BytesIO

from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MinIOClient:
    """Thin wrapper around the MinIO SDK client.

    Initialized once at startup via ``ensure_bucket()``.
    Injected into route handlers via ``Depends(get_minio_client)``.
    """

    def __init__(self) -> None:
        """Initialize the MinIO SDK client with settings from the environment."""
        self._client = Minio(
            endpoint=settings.minio.endpoint,
            access_key=settings.minio.access_key,
            secret_key=settings.minio.secret_key,
            secure=settings.minio.use_ssl,
        )
        self._bucket = settings.minio.bucket_documents
        logger.info(
            "MinIOClient initialized",
            extra={"endpoint": settings.minio.endpoint, "bucket": self._bucket},
        )

    def ensure_bucket(self) -> None:
        """Create the documents bucket if it does not already exist.

        Called once during FastAPI lifespan startup so the application
        is ready to store files immediately after launch.

        Raises:
            S3Error: If the bucket cannot be created due to a permission
                     or connectivity issue.
        """
        try:
            if not self._client.bucket_exists(self._bucket):
                self._client.make_bucket(self._bucket)
                logger.info("MinIO bucket created", extra={"bucket": self._bucket})
            else:
                logger.info("MinIO bucket exists", extra={"bucket": self._bucket})
        except S3Error as exc:
            logger.error(
                "Failed to ensure MinIO bucket",
                extra={"bucket": self._bucket, "error": str(exc)},
            )
            raise

    def ping(self) -> bool:
        """Check connectivity to MinIO by listing buckets.

        Returns:
            bool: True if MinIO is reachable, False otherwise.
        """
        try:
            self._client.list_buckets()
            return True
        except Exception as exc:
            logger.warning("MinIO ping failed", extra={"error": str(exc)})
            return False

    async def upload_file(
        self, data: bytes, object_name: str, content_type: str = "application/octet-stream"
    ) -> str:
        """Upload raw bytes to MinIO.

        Args:
            data:         File content as bytes.
            object_name:  Target object name (path) in the bucket.
            content_type: MIME type of the content.

        Returns:
            str: The object name stored in MinIO.
        """
        self._client.put_object(
            bucket_name=self._bucket,
            object_name=object_name,
            data=BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
        logger.info("File uploaded", extra={"object": object_name, "size": len(data)})
        return object_name

    async def get_presigned_url(self, object_name: str, expiry_hours: int = 24) -> str:
        """Generate a presigned GET URL for temporary object access.

        Args:
            object_name:  Object name in the bucket.
            expiry_hours: URL validity in hours (default: 24).

        Returns:
            str: Presigned URL string.
        """
        from datetime import timedelta

        url = self._client.presigned_get_object(
            bucket_name=self._bucket,
            object_name=object_name,
            expires=timedelta(hours=expiry_hours),
        )
        return url


# ---------------------------------------------------------------------------
# Singleton instance — initialized at startup
# ---------------------------------------------------------------------------
_minio_client: MinIOClient | None = None


def get_minio_client() -> MinIOClient:
    """FastAPI dependency — return the application-level MinIO client.

    Raises:
        RuntimeError: If called before the client has been initialized
                      during application startup.
    """
    if _minio_client is None:
        raise RuntimeError("MinIOClient has not been initialized. Check application startup.")
    return _minio_client


def init_minio_client() -> MinIOClient:
    """Initialize and return the singleton MinIO client.

    Called once from the FastAPI lifespan handler.
    """
    global _minio_client
    _minio_client = MinIOClient()
    _minio_client.ensure_bucket()
    return _minio_client

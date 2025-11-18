"""
File service module.

This module handles file operations using S3-compatible storage (AWS S3 or MinIO),
including generating presigned URLs for direct client-to-storage uploads to avoid
blocking API interactions. The storage backend is determined by configuration settings.
"""

from typing import Optional
from urllib.parse import urlparse, urlunparse

import boto3
from botocore.exceptions import ClientError

from core.logging import get_logger
from core.settings import settings

logger = get_logger(__name__)


class FileServiceError(Exception):
    """Raised when file service operations fail."""

    pass


def replace_url_endpoint(url: str, external_url: Optional[str]) -> str:
    """
    Replace the internal endpoint URL with the external URL for browser access.

    This is necessary when using port forwarding, as presigned URLs generated
    by boto3 will contain the internal endpoint, but browsers need the external
    URL to access via port forwarding.

    Args:
        url: Original URL with internal endpoint
        external_url: External URL to use for replacement (optional)

    Returns:
        str: URL with external endpoint (if configured) or original URL
    """
    if not external_url:
        return url

    try:
        parsed = urlparse(url)
        external_parsed = urlparse(external_url)

        # Replace scheme, netloc (host:port) with external URL
        new_parsed = parsed._replace(
            scheme=external_parsed.scheme, netloc=external_parsed.netloc
        )
        return urlunparse(new_parsed)
    except Exception as e:
        logger.warning(f"Failed to replace URL endpoint, using original: {e}")
        return url


# deactivated for now
# @contextmanager
# def s3_client():
#     """
#     Context manager for S3-compatible client.

#     Yields a configured boto3 S3 client based on settings.

#     Yields:
#         BaseClient: Configured boto3 S3 client

#     Example:
#         with s3_client() as client:
#             response = client.list_objects(Bucket='my-bucket')
#     """
#     client_params = {
#         "service_name": "s3",
#         "region_name": settings.s3_region,
#         "endpoint_url": settings.s3_endpoint_url,
#         "use_ssl": settings.s3_use_ssl,
#         "aws_access_key_id": settings.s3_access_key,
#         "aws_secret_access_key": settings.s3_secret_key,
#     }

#     client = boto3.client(**client_params)
#     try:
#         yield client
#     finally:
#         # boto3 clients don't need explicit cleanup, but we keep the pattern
#         pass


class FileService:
    """File service class for S3-compatible storage operations.

    This class maintains a single boto3 client instance for efficiency.
    The client is thread-safe and reuses connections from boto3's connection pool.
    For standalone operations, use the s3_client() context manager instead.
    """

    def __init__(self):
        """Initialize the FileService with a reusable S3 client."""
        # Settings validation happens in settings.py, so we can trust these are configured
        self.bucket_name = settings.s3_bucket
        self.upload_expiration = settings.s3_upload_expiration
        self.external_url = (
            settings.s3_external_url if settings.s3_external_url else None
        )

        logger.info(f"Using S3-compatible endpoint: {settings.s3_endpoint_url}")
        if self.external_url:
            logger.info(f"External URL for presigned URLs: {self.external_url}")

        # Create a single client instance for reuse across operations
        # boto3 clients are thread-safe and maintain their own connection pool
        client_params = {
            "service_name": "s3",
            "region_name": settings.s3_region,
            "endpoint_url": settings.s3_endpoint_url,
            "use_ssl": settings.s3_use_ssl,
            "aws_access_key_id": settings.s3_access_key,
            "aws_secret_access_key": settings.s3_secret_key,
        }
        self._client = boto3.client(**client_params)

    async def get_upload_link(
        self, filename: str, content_type: Optional[str] = None
    ) -> dict:
        """
        Generate a presigned URL for uploading a file directly to S3-compatible storage.

        This allows clients to upload files directly to storage without going through
        the API, preventing API blocking during large file uploads.

        Args:
            filename: Name of the file to upload.
            content_type: Optional MIME type of the file (e.g., 'text/csv').

        Returns:
            dict: Contains 'upload_link' (presigned URL) and 'fields' (form fields if POST).

        Raises:
            FileServiceError: If URL generation fails.
        """
        try:
            logger.info(f"Generating presigned upload URL for: {filename}")

            # Generate presigned POST URL for direct upload
            # Using POST allows for better control and metadata
            conditions = []
            if content_type:
                conditions.append(["starts-with", "$Content-Type", content_type])

            presigned_post = self._client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=filename,
                Fields={"Content-Type": content_type} if content_type else None,
                Conditions=conditions if conditions else None,
                ExpiresIn=self.upload_expiration,
            )

            # Replace internal endpoint with external URL for browser access
            upload_url = replace_url_endpoint(presigned_post["url"], self.external_url)

            logger.debug(f"Presigned URL generated successfully for: {filename}")

            return {
                "upload_link": upload_url,
                "fields": presigned_post["fields"],
                "filename": filename,
                "expires_in": self.upload_expiration,
            }

        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {filename}: {e}")
            logger.exception("Presigned URL generation error")
            raise FileServiceError(f"Failed to generate upload URL: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error generating presigned URL: {e}")
            logger.exception("Unexpected error in get_upload_link")
            raise FileServiceError(f"Unexpected error: {str(e)}") from e

    async def get_file(self, filename: str) -> dict:
        """
        Generate a presigned URL for downloading a file from S3-compatible storage.

        Args:
            filename: Name of the file to download.

        Returns:
            dict: Contains 'download_link' (presigned URL) and expiration info.

        Raises:
            FileServiceError: If URL generation fails.
        """
        try:
            logger.info(f"Generating presigned download URL for: {filename}")

            # Generate presigned GET URL for direct download
            presigned_url = self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": filename},
                ExpiresIn=self.upload_expiration,  # Reuse expiration setting
            )

            # Replace internal endpoint with external URL for browser access
            download_url = replace_url_endpoint(presigned_url, self.external_url)

            logger.debug(
                f"Presigned download URL generated successfully for: {filename}"
            )

            return {
                "download_link": download_url,
                "filename": filename,
                "expires_in": self.upload_expiration,
            }

        except ClientError as e:
            logger.error(
                f"Failed to generate presigned download URL for {filename}: {e}"
            )
            logger.exception("Presigned URL generation error")
            raise FileServiceError(f"Failed to generate download URL: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error generating presigned download URL: {e}")
            logger.exception("Unexpected error in get_file")
            raise FileServiceError(f"Unexpected error: {str(e)}") from e

    async def get_file_list(self) -> list:
        """
        Get a list of files from the service.

        Returns:
            list: List of file objects, each containing metadata like Key, Size, LastModified, etc.
        """
        try:
            logger.info("Listing files from bucket")
            response = self._client.list_objects(Bucket=self.bucket_name)
            # Extract the Contents list from the boto3 response
            files = response.get("Contents", [])
            logger.debug(f"Found {len(files)} files in bucket")
            return files
        except ClientError as e:
            logger.error(f"Failed to list objects: {e}")
            logger.exception("S3 list objects error")
            raise FileServiceError(f"Failed to list files: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error listing files: {e}")
            logger.exception("Unexpected error in get_file_list")
            raise FileServiceError(f"Unexpected error: {str(e)}") from e

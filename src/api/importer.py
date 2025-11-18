"""
File importer endpoints module.

This module provides endpoints for generating presigned S3 URLs for direct
client-to-S3 file uploads, avoiding API blocking during large file transfers.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.logging import get_logger
from services.file_service import FileService, FileServiceError

router = APIRouter()
logger = get_logger(__name__)


def get_file_service() -> FileService:
    """Dependency injection for the file service."""
    return FileService()


@router.get("/file/upload")
async def get_upload_link(
    filename: str = Query(..., description="Name of the file to upload"),
    content_type: Optional[str] = Query(
        None, description="MIME type of the file (e.g., 'text/csv')"
    ),
    service: FileService = Depends(get_file_service),
) -> dict:
    """
    Get a presigned S3 URL for uploading a file directly to S3.

    This endpoint generates a presigned URL that allows clients to upload files
    directly to S3 without going through the API, preventing API blocking during
    large file uploads.

    Args:
        filename: Name of the file to upload.
        content_type: Optional MIME type of the file.
        service: FileService instance (dependency injection).

    Returns:
        dict: Presigned URL and upload fields for direct S3 upload.

    Raises:
        HTTPException: If URL generation fails.
    """
    try:
        logger.info(f"Requesting upload link for: {filename}")
        result = await service.get_upload_link(filename, content_type)
        return result
    except FileServiceError as e:
        logger.error(f"File service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error generating upload link: {e}")
        logger.exception("Unexpected error in get_upload_link endpoint")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate upload link",
        ) from e


@router.get("/file")
async def get_file(
    filename: str = Query(..., description="Name of the file to download"),
    service: FileService = Depends(get_file_service),
) -> dict:
    """
    Get a presigned S3 URL for downloading a file directly from S3.

    Args:
        filename: Name of the file to download.
        service: FileService instance (dependency injection).

    Returns:
        dict: Presigned URL for direct S3 download.

    Raises:
        HTTPException: If URL generation fails.
    """
    try:
        logger.info(f"Requesting download link for: {filename}")
        result = await service.get_file(filename)
        return result
    except FileServiceError as e:
        logger.error(f"File service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error generating download link: {e}")
        logger.exception("Unexpected error in get_file endpoint")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate download link",
        ) from e


@router.get("/file/list")
async def get_file_list(
    service: FileService = Depends(get_file_service),
) -> list:
    """Get a list of files from the service."""
    try:
        logger.info("Requesting file list")
        result = await service.get_file_list()
        return result
    except FileServiceError as e:
        logger.error(f"File service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error generating file list: {e}")
        logger.exception("Unexpected error in get_file_list endpoint")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate file list",
        ) from e

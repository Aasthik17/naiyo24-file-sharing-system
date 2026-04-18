"""
Download service — validate share access, serve files, and log downloads.
"""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.download import Download
from app.models.share import Share
from app.models.file import File
from app.services.share_service import validate_share_access, increment_download_count
from app.services.storage_service import (
    generate_presigned_url,
    get_file_stream,
    get_file_stream_range,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def process_download(
    db: AsyncSession,
    token: str,
    password: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> dict:
    """
    Validate a share token, generate a presigned download URL,
    log the download, and return download info.
    """
    share, file_obj = await validate_share_access(db, token, password)

    # Generate presigned URL (1 hour expiry)
    download_url = generate_presigned_url(file_obj.storage_url, expires_in=3600)

    # Log download
    download_log = Download(
        file_id=file_obj.id,
        share_id=share.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(download_log)

    # Increment counter
    await increment_download_count(db, share)
    await db.flush()

    logger.info(
        f"Download processed: file={file_obj.original_filename} "
        f"share={token[:8]}... ip={ip_address}"
    )

    return {
        "download_url": download_url,
        "filename": file_obj.original_filename,
        "file_size": file_obj.size,
        "mime_type": file_obj.mime_type,
    }


async def get_direct_stream(
    db: AsyncSession,
    token: str,
    password: Optional[str] = None,
    range_start: Optional[int] = None,
    range_end: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    """
    Validate share and return a streaming file response (for direct download).
    Supports range requests for resume-download.
    Returns a dict with stream metadata.
    """
    share, file_obj = await validate_share_access(db, token, password)

    storage_key = file_obj.storage_url

    if range_start is not None:
        # Partial content (range request)
        stream, content_length, content_range, total_size = get_file_stream_range(
            key=storage_key,
            start_byte=range_start,
            end_byte=range_end,
        )
        result = {
            "stream": stream,
            "content_length": content_length,
            "content_range": content_range,
            "total_size": total_size,
            "filename": file_obj.original_filename,
            "mime_type": file_obj.mime_type or "application/octet-stream",
            "status_code": 206,
        }
    else:
        # Full file
        stream, content_length, content_type = get_file_stream(key=storage_key)
        result = {
            "stream": stream,
            "content_length": content_length,
            "filename": file_obj.original_filename,
            "mime_type": file_obj.mime_type or "application/octet-stream",
            "status_code": 200,
        }

    # Log download
    download_log = Download(
        file_id=file_obj.id,
        share_id=share.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(download_log)
    await increment_download_count(db, share)
    await db.flush()

    return result


async def get_file_head_info(
    db: AsyncSession,
    token: str,
    password: Optional[str] = None,
) -> dict:
    """
    Return file metadata without downloading — used by clients for
    resume-download to know total size before requesting ranges.
    """
    share, file_obj = await validate_share_access(db, token, password)
    return {
        "filename": file_obj.original_filename,
        "file_size": file_obj.size,
        "mime_type": file_obj.mime_type or "application/octet-stream",
        "accept_ranges": "bytes",
    }


async def list_downloads_for_file(
    db: AsyncSession,
    file_id: int,
    user_id: int,
) -> list:
    """List all download logs for a file owned by the given user."""
    from sqlalchemy import select

    # Verify ownership
    result = await db.execute(select(File).where(File.id == file_id))
    file_obj = result.scalar_one_or_none()
    if file_obj is None:
        raise ValueError("File not found")
    if file_obj.uploaded_by != user_id:
        raise PermissionError("You do not own this file")

    result = await db.execute(
        select(Download)
        .where(Download.file_id == file_id)
        .order_by(Download.downloaded_at.desc())
    )
    return result.scalars().all()

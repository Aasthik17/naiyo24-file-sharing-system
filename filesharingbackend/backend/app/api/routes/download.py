"""
Download routes — download via share link with presigned URL or direct stream.
Supports resume-download via HTTP Range headers and HEAD requests.
"""
import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.download_service import (
    process_download,
    get_direct_stream,
    get_file_head_info,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


def _parse_range_header(range_header: str) -> tuple:
    """Parse HTTP Range header. Returns (start, end) or (None, None)."""
    if not range_header:
        return None, None
    match = re.match(r"bytes=(\d+)-(\d*)", range_header)
    if not match:
        return None, None
    start = int(match.group(1))
    end = int(match.group(2)) if match.group(2) else None
    return start, end


# ── GET /{token} — download via presigned URL (redirect) ────────────────────
@router.get(
    "/{token}",
    summary="Download a shared file (redirect to presigned URL)",
)
async def download_file(
    token: str,
    request: Request,
    password: Optional[str] = Query(None, description="Password if share is protected"),
    db: AsyncSession = Depends(get_db),
):
    try:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        result = await process_download(
            db=db,
            token=token,
            password=password,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return RedirectResponse(
            url=result["download_url"],
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ── GET /{token}/direct — direct streaming download ─────────────────────────
@router.get(
    "/{token}/direct",
    summary="Direct streaming download with range support",
)
async def download_direct(
    token: str,
    request: Request,
    password: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    try:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # Parse Range header for resume support
        range_header = request.headers.get("range")
        range_start, range_end = _parse_range_header(range_header)

        result = await get_direct_stream(
            db=db,
            token=token,
            password=password,
            range_start=range_start,
            range_end=range_end,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        headers = {
            "Content-Disposition": f'attachment; filename="{result["filename"]}"',
            "Accept-Ranges": "bytes",
        }

        if result["status_code"] == 206:
            headers["Content-Range"] = result["content_range"]

        def iter_stream():
            stream = result["stream"]
            while True:
                chunk = stream.read(8192)
                if not chunk:
                    break
                yield chunk

        return StreamingResponse(
            iter_stream(),
            status_code=result["status_code"],
            media_type=result["mime_type"],
            headers=headers,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ── HEAD /{token} — file metadata for resume-download clients ───────────────
@router.head(
    "/{token}",
    summary="Get file metadata (HEAD request for resume support)",
)
async def download_head(
    token: str,
    password: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    try:
        info = await get_file_head_info(db, token, password)

        return StreamingResponse(
            iter([]),
            status_code=200,
            media_type=info["mime_type"],
            headers={
                "Content-Length": str(info["file_size"]),
                "Accept-Ranges": info["accept_ranges"],
                "Content-Disposition": f'attachment; filename="{info["filename"]}"',
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

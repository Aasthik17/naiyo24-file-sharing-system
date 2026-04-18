"""
Share service — create, validate, and manage secure share links.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.models.file import File
from app.models.share import Share
from app.utils.file_utils import generate_share_token
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def create_share_link(
    db: AsyncSession,
    file_id: int,
    user_id: int,
    expiry_hours: Optional[int] = None,
    password: Optional[str] = None,
    download_limit: Optional[int] = None,
) -> Share:
    """
    Create a share link for a file owned by the given user.
    """
    # Verify file exists and belongs to user
    result = await db.execute(
        select(File).where(File.id == file_id, File.is_deleted == False)
    )
    file_obj = result.scalar_one_or_none()
    if file_obj is None:
        raise ValueError(f"File {file_id} not found")
    if file_obj.uploaded_by != user_id:
        raise PermissionError("You do not own this file")

    # Generate token
    token = generate_share_token()

    # Compute expiry
    hours = expiry_hours or settings.SHARE_LINK_EXPIRY_HOURS
    expiry_time = datetime.now(timezone.utc) + timedelta(hours=hours)

    # Hash password if provided
    hashed_pw = hash_password(password) if password else None

    share = Share(
        file_id=file_id,
        token=token,
        expiry_time=expiry_time,
        password=hashed_pw,
        download_limit=download_limit,
        download_count=0,
        is_active=True,
    )
    db.add(share)
    await db.flush()
    await db.refresh(share)

    logger.info(f"Share link created: token={token[:8]}... file_id={file_id}")
    return share


async def get_share_by_token(db: AsyncSession, token: str) -> Optional[Share]:
    """Fetch a share record by its token, including the related file."""
    result = await db.execute(
        select(Share)
        .options(selectinload(Share.file))
        .where(Share.token == token)
    )
    return result.scalar_one_or_none()


async def validate_share_access(
    db: AsyncSession,
    token: str,
    password: Optional[str] = None,
) -> tuple:
    """
    Validate a share link:
    - Exists
    - Is active
    - Not expired
    - Download limit not exceeded
    - Password matches (if protected)

    Returns (share, file) tuple on success.
    Raises ValueError with descriptive message on failure.
    """
    share = await get_share_by_token(db, token)

    if share is None:
        raise ValueError("Share link not found")

    if not share.is_active:
        raise ValueError("Share link has been deactivated")

    # Check expiry
    if share.expiry_time and datetime.now(timezone.utc) > share.expiry_time:
        raise ValueError("Share link has expired")

    # Check download limit
    if share.download_limit is not None and share.download_count >= share.download_limit:
        raise ValueError("Download limit reached")

    # Check password
    if share.password:
        if not password:
            raise ValueError("This share link is password protected")
        if not verify_password(password, share.password):
            raise ValueError("Incorrect password")

    # Get file
    file_obj = share.file
    if file_obj is None or file_obj.is_deleted:
        raise ValueError("The shared file has been deleted")

    return share, file_obj


async def increment_download_count(db: AsyncSession, share: Share):
    """Increment download_count for a share link."""
    share.download_count += 1
    await db.flush()


async def deactivate_share(db: AsyncSession, token: str, user_id: int):
    """Deactivate (revoke) a share link. Only the file owner can do this."""
    share = await get_share_by_token(db, token)
    if share is None:
        raise ValueError("Share link not found")

    # Check ownership through the file
    file_obj = share.file
    if file_obj is None or file_obj.uploaded_by != user_id:
        raise PermissionError("You do not own this share link")

    share.is_active = False
    await db.flush()
    logger.info(f"Share link deactivated: {token[:8]}...")


async def get_share_info(db: AsyncSession, token: str) -> dict:
    """Return public info about a share link (no auth required)."""
    share = await get_share_by_token(db, token)
    if share is None:
        raise ValueError("Share link not found")

    file_obj = share.file
    is_expired = (
        share.expiry_time is not None
        and datetime.now(timezone.utc) > share.expiry_time
    )

    return {
        "token": share.token,
        "filename": file_obj.original_filename if file_obj else "unknown",
        "file_size": file_obj.size if file_obj else 0,
        "mime_type": file_obj.mime_type if file_obj else None,
        "expiry_time": share.expiry_time,
        "download_count": share.download_count,
        "download_limit": share.download_limit,
        "is_password_protected": share.password is not None,
        "is_expired": is_expired,
        "created_at": share.created_at,
    }


async def list_user_shares(db: AsyncSession, user_id: int) -> list:
    """List all active shares for files owned by a user."""
    result = await db.execute(
        select(Share)
        .join(File, Share.file_id == File.id)
        .options(selectinload(Share.file))
        .where(File.uploaded_by == user_id, Share.is_active == True)
        .order_by(Share.created_at.desc())
    )
    return result.scalars().all()

"""
Share routes — create share links, get info, list user shares, revoke.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.share_schema import (
    ShareCreateRequest,
    ShareCreateResponse,
    ShareInfoResponse,
)
from app.schemas.user_schema import MessageResponse
from app.services.share_service import (
    create_share_link,
    get_share_info,
    deactivate_share,
    list_user_shares,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ── POST /create — create a share link ───────────────────────────────────────
@router.post(
    "/create",
    response_model=ShareCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a share link for a file",
)
async def create_share(
    body: ShareCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        share = await create_share_link(
            db=db,
            file_id=body.file_id,
            user_id=current_user.id,
            expiry_hours=body.expiry_hours,
            password=body.password,
            download_limit=body.download_limit,
        )

        # Build share URL
        base_url = str(request.base_url).rstrip("/")
        share_url = f"{base_url}/api/download/{share.token}"

        return ShareCreateResponse(
            share_token=share.token,
            share_url=share_url,
            expiry_time=share.expiry_time,
            download_limit=share.download_limit,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ── GET /{token}/info — public share info (no auth) ─────────────────────────
@router.get(
    "/{token}/info",
    response_model=ShareInfoResponse,
    summary="Get public information about a share link",
)
async def share_info(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        info = await get_share_info(db, token)
        return ShareInfoResponse(**info)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ── GET /my — list current user's share links ───────────────────────────────
@router.get(
    "/my",
    summary="List all active share links for the current user",
)
async def my_shares(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    shares = await list_user_shares(db, current_user.id)
    results = []
    for s in shares:
        results.append({
            "token": s.token,
            "file_id": s.file_id,
            "filename": s.file.original_filename if s.file else "unknown",
            "expiry_time": str(s.expiry_time) if s.expiry_time else None,
            "download_count": s.download_count,
            "download_limit": s.download_limit,
            "is_password_protected": s.password is not None,
            "created_at": str(s.created_at),
        })
    return {"shares": results, "total": len(results)}


# ── DELETE /{token} — revoke a share link ────────────────────────────────────
@router.delete(
    "/{token}",
    response_model=MessageResponse,
    summary="Revoke (deactivate) a share link",
)
async def revoke_share(
    token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await deactivate_share(db, token, current_user.id)
        return MessageResponse(message="Share link revoked")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

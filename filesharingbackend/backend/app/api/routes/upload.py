"""
Upload routes — create upload session, upload chunks, finalize, check progress, cancel.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.file import File as FileModel
from app.schemas.file_schema import (
    UploadStartRequest,
    UploadStartResponse,
    ChunkUploadResponse,
    UploadFinalizeRequest,
    UploadFinalizeResponse,
    FileResponse,
    FileListResponse,
    UploadProgressResponse,
)
from app.schemas.user_schema import MessageResponse
from app.services.upload_service import (
    create_upload_session,
    process_chunk_upload,
    finalize_upload,
    get_upload_progress,
    cancel_upload,
)
from app.services.share_service import create_share_link
from app.utils.logger import get_logger
from sqlalchemy import select

logger = get_logger(__name__)

router = APIRouter()


# ── POST /start — create upload session ──────────────────────────────────────
@router.post(
    "/start",
    response_model=UploadStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new chunked upload session",
)
async def start_upload(
    body: UploadStartRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = await create_upload_session(
            user_id=current_user.id,
            filename=body.filename,
            file_size=body.file_size,
            mime_type=body.mime_type,
        )
        return UploadStartResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ── POST /chunk — upload a single chunk ──────────────────────────────────────
@router.post(
    "/chunk",
    response_model=ChunkUploadResponse,
    summary="Upload a single file chunk",
)
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    chunk: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    try:
        chunk_data = await chunk.read()
        result = await process_chunk_upload(
            upload_id=upload_id,
            chunk_index=chunk_index,
            chunk_data=chunk_data,
            user_id=current_user.id,
        )
        return ChunkUploadResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ── POST /finalize — assemble chunks into final file ────────────────────────
@router.post(
    "/finalize",
    response_model=UploadFinalizeResponse,
    summary="Finalize upload — assemble all chunks",
)
async def finalize(
    body: UploadFinalizeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await finalize_upload(
            upload_id=body.upload_id,
            user_id=current_user.id,
        )

        # Create the file record in the database
        file_record = FileModel(
            filename=result["storage_filename"],
            original_filename=result["original_filename"],
            size=result["file_size"],
            mime_type=result["mime_type"],
            storage_url=result["storage_key"],
            uploaded_by=current_user.id,
        )
        db.add(file_record)
        await db.flush()
        await db.refresh(file_record)

        logger.info(
            f"File record created: id={file_record.id} "
            f"name={file_record.original_filename}"
        )

        return UploadFinalizeResponse(
            file_id=file_record.id,
            filename=file_record.filename,
            original_filename=file_record.original_filename,
            size=file_record.size,
            storage_url=file_record.storage_url,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ── GET /progress/{upload_id} — check upload progress ───────────────────────
@router.get(
    "/progress/{upload_id}",
    response_model=UploadProgressResponse,
    summary="Get upload session progress",
)
async def check_progress(
    upload_id: str,
    current_user: User = Depends(get_current_user),
):
    try:
        result = await get_upload_progress(upload_id, current_user.id)
        return UploadProgressResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ── DELETE /cancel/{upload_id} — cancel upload session ───────────────────────
@router.delete(
    "/cancel/{upload_id}",
    response_model=MessageResponse,
    summary="Cancel an in-progress upload",
)
async def cancel(
    upload_id: str,
    current_user: User = Depends(get_current_user),
):
    try:
        await cancel_upload(upload_id, current_user.id)
        return MessageResponse(message="Upload cancelled and cleaned up")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ── GET /files — list user's uploaded files ──────────────────────────────────
@router.get(
    "/files",
    response_model=FileListResponse,
    summary="List all files uploaded by the current user",
)
async def list_files(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FileModel)
        .where(
            FileModel.uploaded_by == current_user.id,
            FileModel.is_deleted == False,
        )
        .order_by(FileModel.created_at.desc())
    )
    files = result.scalars().all()
    return FileListResponse(
        files=[FileResponse.model_validate(f) for f in files],
        total=len(files),
    )


# ── POST /simple — simple single-file upload ─────────────────────────────────
@router.post(
    "/simple",
    summary="Simple single-file upload for demo purposes",
)
async def simple_upload(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.services.storage_service import get_s3_client, ensure_bucket_exists
    from app.utils.file_utils import generate_storage_filename
    from app.core.config import settings

    ensure_bucket_exists()

    safe_filename = file.filename
    storage_filename = generate_storage_filename(safe_filename)

    key = f"uploads/simple/{storage_filename}"

    client = get_s3_client()
    file_data = await file.read()
    client.put_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=key,
        Body=file_data,
        ContentType=file.content_type,
    )

    file_record = FileModel(
        filename=storage_filename,
        original_filename=safe_filename,
        size=len(file_data),
        mime_type=file.content_type,
        storage_url=key,
        uploaded_by=current_user.id,
    )
    db.add(file_record)
    await db.flush()
    await db.refresh(file_record)

    share = await create_share_link(
        db=db,
        file_id=file_record.id,
        user_id=current_user.id,
    )

    base_url = str(request.base_url).rstrip("/")
    share_url = f"{base_url}/api/download/{share.token}"

    return {"link": share_url}

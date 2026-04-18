"""
Upload service — manages upload sessions via Redis, coordinates chunk uploads
with the storage service, and finalizes uploads into the database.
"""
import json
from typing import Optional, List
from fastapi.concurrency import run_in_threadpool

import redis.asyncio as aioredis

from app.core.config import settings
from app.utils.logger import get_logger
from app.utils.chunk_handler import calculate_total_chunks, validate_file_size, validate_chunk_index
from app.utils.file_utils import (
    sanitize_filename,
    generate_storage_filename,
    generate_upload_id,
    detect_mime_type,
)
from app.services.storage_service import (
    upload_chunk_to_storage,
    assemble_chunks_to_final,
    ensure_bucket_exists,
    delete_upload_session_files,
)

logger = get_logger(__name__)


# ── Redis Connection ──────────────────────────────────────────────────────────
_redis: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Get or create a shared Redis connection."""
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )
    return _redis


def _session_key(upload_id: str) -> str:
    return f"upload_session:{upload_id}"


# ── Create Upload Session ─────────────────────────────────────────────────────
async def create_upload_session(
    user_id: int,
    filename: str,
    file_size: int,
    mime_type: Optional[str] = None,
) -> dict:
    """
    Validate the upload request, create a session in Redis, and return session info.
    """
    # Validate file size
    if not validate_file_size(file_size):
        raise ValueError(
            f"File size {file_size} exceeds maximum allowed "
            f"({settings.MAX_FILE_SIZE_BYTES} bytes)"
        )

    # Ensure bucket exists
    ensure_bucket_exists()

    upload_id = generate_upload_id()
    safe_filename = sanitize_filename(filename)
    storage_filename = generate_storage_filename(safe_filename)
    total_chunks = calculate_total_chunks(file_size)
    resolved_mime = mime_type or detect_mime_type(safe_filename)

    session_data = {
        "upload_id": upload_id,
        "user_id": user_id,
        "original_filename": safe_filename,
        "storage_filename": storage_filename,
        "file_size": file_size,
        "mime_type": resolved_mime,
        "chunk_size": settings.CHUNK_SIZE_BYTES,
        "total_chunks": total_chunks,
        "uploaded_chunks": json.dumps([]),  # list of completed chunk indices
        "status": "in_progress",
    }

    r = await get_redis()
    key = _session_key(upload_id)
    await r.hset(key, mapping=session_data)
    await r.expire(key, settings.UPLOAD_SESSION_TTL_SECONDS)

    logger.info(
        f"Upload session created: {upload_id} | "
        f"file={safe_filename} size={file_size} chunks={total_chunks}"
    )

    return {
        "upload_id": upload_id,
        "filename": safe_filename,
        "file_size": file_size,
        "chunk_size": settings.CHUNK_SIZE_BYTES,
        "total_chunks": total_chunks,
    }


# ── Upload Chunk ──────────────────────────────────────────────────────────────
async def process_chunk_upload(
    upload_id: str,
    chunk_index: int,
    chunk_data: bytes,
    user_id: int,
) -> dict:
    """
    Validate and store a single chunk. Updates Redis session state.
    """
    r = await get_redis()
    key = _session_key(upload_id)

    session = await r.hgetall(key)
    if not session:
        raise ValueError(f"Upload session '{upload_id}' not found or expired")

    if int(session["user_id"]) != user_id:
        raise PermissionError("You do not own this upload session")

    if session["status"] != "in_progress":
        raise ValueError(f"Upload session is '{session['status']}', not in_progress")

    total_chunks = int(session["total_chunks"])
    if not validate_chunk_index(chunk_index, total_chunks):
        raise ValueError(
            f"Invalid chunk index {chunk_index}. Must be 0..{total_chunks - 1}"
        )

    uploaded_chunks: List[int] = json.loads(session["uploaded_chunks"])
    if chunk_index in uploaded_chunks:
        raise ValueError(f"Chunk {chunk_index} already uploaded")

    # Upload to S3/MinIO
    await run_in_threadpool(
        upload_chunk_to_storage,
        user_id=user_id,
        upload_id=upload_id,
        chunk_index=chunk_index,
        data=chunk_data,
    )

    # Update session
    uploaded_chunks.append(chunk_index)
    uploaded_chunks.sort()
    await r.hset(key, "uploaded_chunks", json.dumps(uploaded_chunks))
    # Reset TTL on activity
    await r.expire(key, settings.UPLOAD_SESSION_TTL_SECONDS)

    logger.debug(
        f"Chunk {chunk_index}/{total_chunks - 1} uploaded for session {upload_id}"
    )

    return {
        "upload_id": upload_id,
        "chunk_index": chunk_index,
        "received_size": len(chunk_data),
    }


# ── Get Upload Progress ──────────────────────────────────────────────────────
async def get_upload_progress(upload_id: str, user_id: int) -> dict:
    """Return the current upload progress for a session."""
    r = await get_redis()
    key = _session_key(upload_id)
    session = await r.hgetall(key)

    if not session:
        raise ValueError(f"Upload session '{upload_id}' not found or expired")

    if int(session["user_id"]) != user_id:
        raise PermissionError("You do not own this upload session")

    total_chunks = int(session["total_chunks"])
    uploaded_chunks: List[int] = json.loads(session["uploaded_chunks"])
    remaining = total_chunks - len(uploaded_chunks)
    progress = (len(uploaded_chunks) / total_chunks * 100) if total_chunks > 0 else 0

    return {
        "upload_id": upload_id,
        "filename": session["original_filename"],
        "total_chunks": total_chunks,
        "uploaded_chunks": uploaded_chunks,
        "remaining_chunks": remaining,
        "progress_percent": round(progress, 2),
    }


# ── Finalize Upload ──────────────────────────────────────────────────────────
async def finalize_upload(upload_id: str, user_id: int) -> dict:
    """
    Verify all chunks are uploaded, assemble the final file in S3,
    and return metadata needed to create the DB record.
    """
    r = await get_redis()
    key = _session_key(upload_id)
    session = await r.hgetall(key)

    if not session:
        raise ValueError(f"Upload session '{upload_id}' not found or expired")

    if int(session["user_id"]) != user_id:
        raise PermissionError("You do not own this upload session")

    if session["status"] != "in_progress":
        raise ValueError(f"Upload session is '{session['status']}', cannot finalize")

    total_chunks = int(session["total_chunks"])
    uploaded_chunks: List[int] = json.loads(session["uploaded_chunks"])

    if len(uploaded_chunks) != total_chunks:
        missing = set(range(total_chunks)) - set(uploaded_chunks)
        raise ValueError(
            f"Cannot finalize: {len(missing)} chunks missing — {sorted(missing)}"
        )

    # Mark as finalizing to prevent duplicate finalizations
    await r.hset(key, "status", "finalizing")

    # Assemble in S3
    storage_filename = session["storage_filename"]
    final_key = await run_in_threadpool(
        assemble_chunks_to_final,
        user_id=user_id,
        upload_id=upload_id,
        total_chunks=total_chunks,
        final_filename=storage_filename,
    )

    # Mark complete and set short TTL for cleanup
    await r.hset(key, mapping={"status": "completed", "storage_key": final_key})
    await r.expire(key, 300)  # keep for 5 min then auto-delete

    logger.info(f"Upload {upload_id} finalized → {final_key}")

    return {
        "original_filename": session["original_filename"],
        "storage_filename": storage_filename,
        "storage_key": final_key,
        "file_size": int(session["file_size"]),
        "mime_type": session["mime_type"],
    }


# ── Cancel / Cleanup ─────────────────────────────────────────────────────────
async def cancel_upload(upload_id: str, user_id: int):
    """Cancel an in-progress upload, remove chunks from storage and Redis."""
    r = await get_redis()
    key = _session_key(upload_id)
    session = await r.hgetall(key)

    if not session:
        raise ValueError(f"Upload session '{upload_id}' not found or expired")

    if int(session["user_id"]) != user_id:
        raise PermissionError("You do not own this upload session")

    # Cleanup storage
    await run_in_threadpool(delete_upload_session_files, user_id, upload_id)

    # Remove from Redis
    await r.delete(key)
    logger.info(f"Upload session {upload_id} cancelled and cleaned up")

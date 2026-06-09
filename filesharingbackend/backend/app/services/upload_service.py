"""
Upload service — manages upload sessions, coordinates chunk uploads
with the storage service, and finalizes uploads into the database.

Uses in-memory dict for session tracking (single-server setup).
"""
import json
import time
from typing import Optional, List, Dict

from fastapi.concurrency import run_in_threadpool

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
    ensure_upload_dir,
    delete_upload_session_files,
)

logger = get_logger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# Session Backend — In-Memory
# ══════════════════════════════════════════════════════════════════════════════

_memory_sessions: Dict[str, dict] = {}
_memory_session_expiry: Dict[str, float] = {}


def _session_key(upload_id: str) -> str:
    return f"upload_session:{upload_id}"


def _cleanup_expired_memory_sessions():
    """Remove expired in-memory sessions."""
    now = time.time()
    expired = [k for k, v in _memory_session_expiry.items() if v < now]
    for k in expired:
        _memory_sessions.pop(k, None)
        _memory_session_expiry.pop(k, None)


# ── Session Operations ────────────────────────────────────────────────────────
async def _save_session(upload_id: str, data: dict, ttl: int):
    """Save session to in-memory store."""
    key = _session_key(upload_id)
    _cleanup_expired_memory_sessions()
    _memory_sessions[key] = data.copy()
    _memory_session_expiry[key] = time.time() + ttl


async def _get_session(upload_id: str) -> Optional[dict]:
    """Get session from in-memory store."""
    key = _session_key(upload_id)
    _cleanup_expired_memory_sessions()
    session = _memory_sessions.get(key)
    return session.copy() if session else None


async def _update_session_field(upload_id: str, field: str, value, ttl: int = None):
    """Update a single field in the session."""
    key = _session_key(upload_id)
    if key in _memory_sessions:
        _memory_sessions[key][field] = value
        if ttl:
            _memory_session_expiry[key] = time.time() + ttl


async def _update_session_fields(upload_id: str, fields: dict, ttl: int = None):
    """Update multiple fields in the session."""
    key = _session_key(upload_id)
    if key in _memory_sessions:
        _memory_sessions[key].update(fields)
        if ttl:
            _memory_session_expiry[key] = time.time() + ttl


async def _delete_session(upload_id: str):
    """Delete a session from in-memory store."""
    key = _session_key(upload_id)
    _memory_sessions.pop(key, None)
    _memory_session_expiry.pop(key, None)


# ══════════════════════════════════════════════════════════════════════════════
# Upload Service — Business Logic
# ══════════════════════════════════════════════════════════════════════════════

# ── Create Upload Session ─────────────────────────────────────────────────────
async def create_upload_session(
    user_id: int,
    filename: str,
    file_size: int,
    mime_type: Optional[str] = None,
) -> dict:
    """
    Validate the upload request, create a session, and return session info.
    """
    # Validate file size
    if not validate_file_size(file_size):
        raise ValueError(
            f"File size {file_size} exceeds maximum allowed "
            f"({settings.MAX_FILE_SIZE_BYTES} bytes)"
        )

    # Ensure upload directory exists
    ensure_upload_dir()

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
        "uploaded_chunks": [],
        "status": "in_progress",
    }

    await _save_session(upload_id, session_data, settings.UPLOAD_SESSION_TTL_SECONDS)

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
    Validate and store a single chunk. Updates session state.
    """
    session = await _get_session(upload_id)
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

    uploaded_chunks = session.get("uploaded_chunks", [])
    if isinstance(uploaded_chunks, str):
        uploaded_chunks = json.loads(uploaded_chunks)
    uploaded_chunks = [int(c) for c in uploaded_chunks]

    if chunk_index in uploaded_chunks:
        raise ValueError(f"Chunk {chunk_index} already uploaded")

    # Upload chunk to local storage
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
    await _update_session_field(
        upload_id, "uploaded_chunks", uploaded_chunks,
        ttl=settings.UPLOAD_SESSION_TTL_SECONDS,
    )

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
    session = await _get_session(upload_id)
    if not session:
        raise ValueError(f"Upload session '{upload_id}' not found or expired")

    if int(session["user_id"]) != user_id:
        raise PermissionError("You do not own this upload session")

    total_chunks = int(session["total_chunks"])
    uploaded_chunks = session.get("uploaded_chunks", [])
    if isinstance(uploaded_chunks, str):
        uploaded_chunks = json.loads(uploaded_chunks)
    uploaded_chunks = [int(c) for c in uploaded_chunks]

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
    Verify all chunks are uploaded, assemble the final file,
    and return metadata needed to create the DB record.
    """
    session = await _get_session(upload_id)
    if not session:
        raise ValueError(f"Upload session '{upload_id}' not found or expired")

    if int(session["user_id"]) != user_id:
        raise PermissionError("You do not own this upload session")

    if session["status"] != "in_progress":
        raise ValueError(f"Upload session is '{session['status']}', cannot finalize")

    total_chunks = int(session["total_chunks"])
    uploaded_chunks = session.get("uploaded_chunks", [])
    if isinstance(uploaded_chunks, str):
        uploaded_chunks = json.loads(uploaded_chunks)
    uploaded_chunks = [int(c) for c in uploaded_chunks]

    if len(uploaded_chunks) != total_chunks:
        missing = set(range(total_chunks)) - set(uploaded_chunks)
        raise ValueError(
            f"Cannot finalize: {len(missing)} chunks missing — {sorted(missing)}"
        )

    # Mark as finalizing to prevent duplicate finalizations
    await _update_session_field(upload_id, "status", "finalizing")

    # Assemble on disk
    storage_filename = session["storage_filename"]
    final_key = await run_in_threadpool(
        assemble_chunks_to_final,
        user_id=user_id,
        upload_id=upload_id,
        total_chunks=total_chunks,
        final_filename=storage_filename,
    )

    # Mark complete and set short TTL for cleanup
    await _update_session_fields(
        upload_id,
        {"status": "completed", "storage_key": final_key},
        ttl=300,  # keep for 5 min then auto-delete
    )

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
    """Cancel an in-progress upload, remove chunks from storage and session store."""
    session = await _get_session(upload_id)
    if not session:
        raise ValueError(f"Upload session '{upload_id}' not found or expired")

    if int(session["user_id"]) != user_id:
        raise PermissionError("You do not own this upload session")

    # Cleanup storage
    await run_in_threadpool(delete_upload_session_files, user_id, upload_id)

    # Remove session
    await _delete_session(upload_id)
    logger.info(f"Upload session {upload_id} cancelled and cleaned up")

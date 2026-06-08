"""
Local filesystem storage service — handles all file storage operations.
Stores files on the local filesystem under settings.UPLOAD_DIR.
No external dependencies (no boto3/S3/MinIO needed).
"""
import os
import shutil
from pathlib import Path
from typing import Optional, Tuple, BinaryIO

import aiofiles
import aiofiles.os

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ── Base upload directory ─────────────────────────────────────────────────────
_upload_dir = Path(settings.UPLOAD_DIR).resolve()


def ensure_upload_dir():
    """Create the base upload directory if it doesn't exist."""
    _upload_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Upload directory verified: {_upload_dir} ✓")


def _chunk_dir(user_id: int, upload_id: str) -> Path:
    """Return the directory where chunks for an upload session are stored."""
    return _upload_dir / "chunks" / str(user_id) / upload_id


def _final_file_path(user_id: int, upload_id: str, filename: str) -> Path:
    """Return the final assembled file path."""
    return _upload_dir / "files" / str(user_id) / upload_id / filename


# ── Upload Operations ─────────────────────────────────────────────────────────
def upload_chunk_to_storage(
    user_id: int,
    upload_id: str,
    chunk_index: int,
    data: bytes,
) -> str:
    """
    Upload a single chunk to local storage.
    Stored at: uploads/chunks/{user_id}/{upload_id}/{chunk_index}
    Returns the storage key (relative path).
    """
    chunk_path = _chunk_dir(user_id, upload_id)
    chunk_path.mkdir(parents=True, exist_ok=True)

    file_path = chunk_path / str(chunk_index)
    file_path.write_bytes(data)

    key = f"chunks/{user_id}/{upload_id}/{chunk_index}"
    logger.debug(f"Chunk {chunk_index} uploaded → {key}")
    return key


def assemble_chunks_to_final(
    user_id: int,
    upload_id: str,
    total_chunks: int,
    final_filename: str,
) -> str:
    """
    Concatenate all chunk files into a single final file.
    Reads chunks sequentially and writes to the final file.
    Final location: uploads/files/{user_id}/{upload_id}/{final_filename}
    Returns the storage key (relative path).
    """
    final_path = _final_file_path(user_id, upload_id, final_filename)
    final_path.parent.mkdir(parents=True, exist_ok=True)

    chunk_dir = _chunk_dir(user_id, upload_id)

    try:
        with open(final_path, "wb") as final_file:
            for i in range(total_chunks):
                chunk_file = chunk_dir / str(i)
                if not chunk_file.exists():
                    raise FileNotFoundError(f"Chunk {i} not found at {chunk_file}")
                with open(chunk_file, "rb") as cf:
                    # Read in 8KB buffers to avoid loading entire chunk into RAM
                    while True:
                        buf = cf.read(8192)
                        if not buf:
                            break
                        final_file.write(buf)

        logger.info(f"Final file assembled → files/{user_id}/{upload_id}/{final_filename}")

    except Exception as e:
        logger.error(f"Failed to assemble chunks: {e}")
        # Clean up partial file
        if final_path.exists():
            final_path.unlink()
        raise

    # Cleanup chunk files
    try:
        shutil.rmtree(chunk_dir)
        logger.debug(f"Cleaned up chunk directory: {chunk_dir}")
    except OSError as e:
        logger.warning(f"Failed to cleanup chunks: {e}")

    storage_key = f"files/{user_id}/{upload_id}/{final_filename}"
    return storage_key


# ── Download Operations ───────────────────────────────────────────────────────
def get_file_full_path(storage_key: str) -> Path:
    """Resolve a storage key to an absolute file path."""
    return _upload_dir / storage_key


def get_file_stream(key: str) -> Tuple[BinaryIO, int, str]:
    """
    Get a file stream for download.
    Returns (file_handle, content_length, content_type).
    Caller is responsible for closing the file handle.
    """
    file_path = get_file_full_path(key)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {key}")

    file_size = file_path.stat().st_size
    file_handle = open(file_path, "rb")

    return file_handle, file_size, "application/octet-stream"


def get_file_stream_range(
    key: str,
    start_byte: int,
    end_byte: Optional[int] = None,
) -> Tuple[BinaryIO, int, str, int]:
    """
    Get a partial (range) file stream for resume-download support.
    Returns (file_handle, content_length, content_range, total_size).
    Caller is responsible for closing the file handle.
    """
    file_path = get_file_full_path(key)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {key}")

    total_size = file_path.stat().st_size

    if end_byte is None or end_byte >= total_size:
        end_byte = total_size - 1

    file_handle = open(file_path, "rb")
    file_handle.seek(start_byte)

    content_length = end_byte - start_byte + 1
    content_range = f"bytes {start_byte}-{end_byte}/{total_size}"

    return file_handle, content_length, content_range, total_size


# ── Delete Operations ─────────────────────────────────────────────────────────
def delete_file_from_storage(key: str) -> bool:
    """Delete a file from storage. Returns True on success."""
    file_path = get_file_full_path(key)
    try:
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted from storage: {key}")
            # Try to remove empty parent directories
            _cleanup_empty_parents(file_path.parent)
            return True
        else:
            logger.warning(f"File not found for deletion: {key}")
            return False
    except OSError as e:
        logger.error(f"Failed to delete {key}: {e}")
        return False


def delete_upload_session_files(user_id: int, upload_id: str):
    """Delete all chunk and final files for a given upload session."""
    # Delete chunks
    chunk_dir = _chunk_dir(user_id, upload_id)
    if chunk_dir.exists():
        try:
            shutil.rmtree(chunk_dir)
            logger.info(f"Cleaned up chunks for session {upload_id}")
        except OSError as e:
            logger.error(f"Failed to cleanup chunks for {upload_id}: {e}")

    # Delete final files directory
    final_dir = _upload_dir / "files" / str(user_id) / upload_id
    if final_dir.exists():
        try:
            shutil.rmtree(final_dir)
            logger.info(f"Cleaned up final files for session {upload_id}")
        except OSError as e:
            logger.error(f"Failed to cleanup final files for {upload_id}: {e}")


def _cleanup_empty_parents(directory: Path):
    """Remove empty parent directories up to the upload root."""
    try:
        while directory != _upload_dir and directory.exists():
            if any(directory.iterdir()):
                break  # Not empty
            directory.rmdir()
            directory = directory.parent
    except OSError:
        pass  # Ignore cleanup errors


# ── Simple Upload ─────────────────────────────────────────────────────────────
def simple_upload_file(filename: str, data: bytes) -> str:
    """
    Store a file via simple (non-chunked) upload.
    Returns the storage key.
    """
    from app.utils.file_utils import generate_storage_filename

    storage_filename = generate_storage_filename(filename)
    file_dir = _upload_dir / "files" / "simple"
    file_dir.mkdir(parents=True, exist_ok=True)

    file_path = file_dir / storage_filename
    file_path.write_bytes(data)

    storage_key = f"files/simple/{storage_filename}"
    logger.info(f"Simple upload stored → {storage_key}")
    return storage_key

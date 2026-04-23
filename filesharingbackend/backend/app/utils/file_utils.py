"""
File utility helpers — MIME detection, safe filenames, token generation.
"""
import mimetypes
import re
import secrets
import uuid
from datetime import datetime


def detect_mime_type(filename: str) -> str:
    """Detect MIME type from filename extension, fallback to binary stream."""
    mime, _ = mimetypes.guess_type(filename)
    return mime or "application/octet-stream"


def sanitize_filename(filename: str) -> str:
    """
    Remove dangerous characters from a filename while preserving the extension.
    """
    # Strip path components
    filename = filename.replace("\\", "/").split("/")[-1]
    # Remove non-alphanumeric except dots, hyphens, underscores
    filename = re.sub(r"[^\w\.\-]", "_", filename)
    # Collapse multiple underscores
    filename = re.sub(r"_+", "_", filename).strip("_")
    return filename or "unnamed_file"


def generate_storage_filename(original_filename: str) -> str:
    """Generate a unique filename for storage to prevent collisions."""
    ext = ""
    if "." in original_filename:
        ext = "." + original_filename.rsplit(".", 1)[-1].lower()
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:12]
    return f"{timestamp}_{unique_id}{ext}"


def generate_share_token(length: int = 8) -> str:
    """Generate a cryptographically secure share token."""
    return secrets.token_urlsafe(length)


def generate_upload_id() -> str:
    """Generate a unique upload session identifier."""
    return uuid.uuid4().hex


def format_file_size(size_bytes: int) -> str:
    """Human-readable file size."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"

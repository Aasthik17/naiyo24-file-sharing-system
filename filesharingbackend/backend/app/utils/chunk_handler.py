"""
Chunk math & validation utilities for chunked file uploads.
"""
import math
from app.core.config import settings


def calculate_total_chunks(file_size: int, chunk_size: int = None) -> int:
    """Calculate the number of chunks for a given file size."""
    chunk_size = chunk_size or settings.CHUNK_SIZE_BYTES
    return math.ceil(file_size / chunk_size)


def get_chunk_offset(chunk_index: int, chunk_size: int = None) -> int:
    """Return the byte offset for a given chunk index."""
    chunk_size = chunk_size or settings.CHUNK_SIZE_BYTES
    return chunk_index * chunk_size


def get_expected_chunk_size(
    chunk_index: int,
    total_chunks: int,
    file_size: int,
    chunk_size: int = None,
) -> int:
    """
    Return the expected byte size for a specific chunk.
    The last chunk may be smaller than chunk_size.
    """
    chunk_size = chunk_size or settings.CHUNK_SIZE_BYTES
    if chunk_index == total_chunks - 1:
        remainder = file_size % chunk_size
        return remainder if remainder != 0 else chunk_size
    return chunk_size


def validate_chunk_index(chunk_index: int, total_chunks: int) -> bool:
    """Check that a chunk index is within valid range."""
    return 0 <= chunk_index < total_chunks


def validate_file_size(file_size: int) -> bool:
    """Check that file size does not exceed the configured maximum."""
    return 0 < file_size <= settings.MAX_FILE_SIZE_BYTES

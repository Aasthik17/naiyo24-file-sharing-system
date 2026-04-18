"""
Pydantic schemas for file upload endpoints.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ── Upload Session ────────────────────────────────────────────────────────────
class UploadStartRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=500)
    file_size: int = Field(..., gt=0, description="Total file size in bytes")
    mime_type: Optional[str] = None


class UploadStartResponse(BaseModel):
    upload_id: str
    filename: str
    file_size: int
    chunk_size: int
    total_chunks: int
    message: str = "Upload session created"


class ChunkUploadResponse(BaseModel):
    upload_id: str
    chunk_index: int
    received_size: int
    message: str = "Chunk uploaded"


class UploadFinalizeRequest(BaseModel):
    upload_id: str


class UploadFinalizeResponse(BaseModel):
    file_id: int
    filename: str
    original_filename: str
    size: int
    storage_url: str
    message: str = "Upload finalized"


# ── File Info ─────────────────────────────────────────────────────────────────
class FileResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    size: int
    mime_type: Optional[str]
    created_at: datetime
    is_deleted: bool

    model_config = {"from_attributes": True}


class FileListResponse(BaseModel):
    files: List[FileResponse]
    total: int


class UploadProgressResponse(BaseModel):
    upload_id: str
    filename: str
    total_chunks: int
    uploaded_chunks: List[int]
    remaining_chunks: int
    progress_percent: float

"""
Pydantic schemas for share-link and download endpoints.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Share Creation ────────────────────────────────────────────────────────────
class ShareCreateRequest(BaseModel):
    file_id: int
    expiry_hours: Optional[int] = Field(None, ge=1, le=720, description="Link expiry in hours (default from config)")
    password: Optional[str] = Field(None, min_length=4, max_length=128, description="Optional password protection")
    download_limit: Optional[int] = Field(None, ge=1, description="Max number of downloads allowed")


class ShareCreateResponse(BaseModel):
    share_token: str
    share_url: str
    expiry_time: Optional[datetime]
    download_limit: Optional[int]
    message: str = "Share link created"


# ── Share Info ────────────────────────────────────────────────────────────────
class ShareInfoResponse(BaseModel):
    token: str
    filename: str
    file_size: int
    mime_type: Optional[str]
    expiry_time: Optional[datetime]
    download_count: int
    download_limit: Optional[int]
    is_password_protected: bool
    is_expired: bool
    created_at: datetime


# ── Share Validation ──────────────────────────────────────────────────────────
class SharePasswordRequest(BaseModel):
    password: str


# ── Download Tracking ─────────────────────────────────────────────────────────
class DownloadLogResponse(BaseModel):
    id: int
    file_id: int
    share_id: Optional[int]
    ip_address: Optional[str]
    downloaded_at: datetime

    model_config = {"from_attributes": True}

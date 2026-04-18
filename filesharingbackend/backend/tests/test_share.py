"""
Tests for Share and Download API endpoints.
Covers: create share, get info, revoke, download.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.share import Share
from app.models.file import File as FileModel


# ── Fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.is_active = True
    return user


@pytest.fixture
def client(mock_user):
    """Create test client with mocked dependencies."""

    async def override_current_user():
        return mock_user

    async def override_db():
        db = AsyncMock()
        yield db

    app.dependency_overrides[get_current_user] = override_current_user
    app.dependency_overrides[get_db] = override_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ── Share Tests ───────────────────────────────────────────────────────────────
class TestShareCreate:
    """Test POST /api/share/create"""

    @patch("app.api.routes.share.create_share_link")
    def test_create_share_success(self, mock_create, client):
        mock_share = MagicMock(spec=Share)
        mock_share.token = "abc123token"
        mock_share.expiry_time = datetime.now(timezone.utc) + timedelta(hours=72)
        mock_share.download_limit = None
        mock_create.return_value = mock_share

        response = client.post(
            "/api/share/create",
            json={"file_id": 1},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["share_token"] == "abc123token"
        assert "share_url" in data

    @patch("app.api.routes.share.create_share_link")
    def test_create_share_with_password(self, mock_create, client):
        mock_share = MagicMock(spec=Share)
        mock_share.token = "protected_token"
        mock_share.expiry_time = datetime.now(timezone.utc) + timedelta(hours=24)
        mock_share.download_limit = 5
        mock_create.return_value = mock_share

        response = client.post(
            "/api/share/create",
            json={
                "file_id": 1,
                "expiry_hours": 24,
                "password": "secret123",
                "download_limit": 5,
            },
        )

        assert response.status_code == 201

    @patch("app.api.routes.share.create_share_link")
    def test_create_share_file_not_found(self, mock_create, client):
        mock_create.side_effect = ValueError("File 999 not found")

        response = client.post(
            "/api/share/create",
            json={"file_id": 999},
        )

        assert response.status_code == 404

    @patch("app.api.routes.share.create_share_link")
    def test_create_share_not_owner(self, mock_create, client):
        mock_create.side_effect = PermissionError("You do not own this file")

        response = client.post(
            "/api/share/create",
            json={"file_id": 2},
        )

        assert response.status_code == 403


class TestShareInfo:
    """Test GET /api/share/{token}/info"""

    @patch("app.api.routes.share.get_share_info")
    def test_get_share_info_success(self, mock_info, client):
        mock_info.return_value = {
            "token": "abc123",
            "filename": "test.pdf",
            "file_size": 1024000,
            "mime_type": "application/pdf",
            "expiry_time": datetime.now(timezone.utc) + timedelta(hours=48),
            "download_count": 3,
            "download_limit": 10,
            "is_password_protected": False,
            "is_expired": False,
            "created_at": datetime.now(timezone.utc),
        }

        response = client.get("/api/share/abc123/info")

        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.pdf"
        assert data["is_expired"] is False

    @patch("app.api.routes.share.get_share_info")
    def test_get_share_info_not_found(self, mock_info, client):
        mock_info.side_effect = ValueError("Share link not found")

        response = client.get("/api/share/nonexistent/info")
        assert response.status_code == 404


class TestShareRevoke:
    """Test DELETE /api/share/{token}"""

    @patch("app.api.routes.share.deactivate_share")
    def test_revoke_share_success(self, mock_deactivate, client):
        mock_deactivate.return_value = None

        response = client.delete("/api/share/abc123")

        assert response.status_code == 200
        assert response.json()["message"] == "Share link revoked"

    @patch("app.api.routes.share.deactivate_share")
    def test_revoke_share_not_owner(self, mock_deactivate, client):
        mock_deactivate.side_effect = PermissionError("You do not own this share link")

        response = client.delete("/api/share/abc123")
        assert response.status_code == 403


# ── Download Tests ────────────────────────────────────────────────────────────
class TestDownload:
    """Test GET /api/download/{token}"""

    @patch("app.api.routes.download.process_download")
    def test_download_redirect(self, mock_process, client):
        mock_process.return_value = {
            "download_url": "https://minio.local/presigned-url",
            "filename": "test.pdf",
            "file_size": 1024000,
            "mime_type": "application/pdf",
        }

        response = client.get(
            "/api/download/abc123",
            follow_redirects=False,
        )

        assert response.status_code == 307
        assert "presigned-url" in response.headers.get("location", "")

    @patch("app.api.routes.download.process_download")
    def test_download_expired(self, mock_process, client):
        mock_process.side_effect = ValueError("Share link has expired")

        response = client.get("/api/download/expired_token")
        assert response.status_code == 403

    @patch("app.api.routes.download.process_download")
    def test_download_wrong_password(self, mock_process, client):
        mock_process.side_effect = ValueError("Incorrect password")

        response = client.get("/api/download/protected_token?password=wrong")
        assert response.status_code == 403

    @patch("app.api.routes.download.process_download")
    def test_download_limit_reached(self, mock_process, client):
        mock_process.side_effect = ValueError("Download limit reached")

        response = client.get("/api/download/limited_token")
        assert response.status_code == 403


class TestDownloadHead:
    """Test HEAD /api/download/{token}"""

    @patch("app.api.routes.download.get_file_head_info")
    def test_head_success(self, mock_head, client):
        mock_head.return_value = {
            "filename": "test.pdf",
            "file_size": 1024000,
            "mime_type": "application/pdf",
            "accept_ranges": "bytes",
        }

        response = client.head("/api/download/abc123")

        assert response.status_code == 200
        assert response.headers.get("accept-ranges") == "bytes"
        assert response.headers.get("content-length") == "1024000"

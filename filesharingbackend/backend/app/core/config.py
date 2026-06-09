from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "FileShareSystem"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "changeme_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "filesharingsystem"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/filesharingsystem"


    # Public URL (used in share links so they're reachable from other devices)
    # Set this to your machine's LAN IP or public domain, e.g. "http://192.168.1.5:8000"
    # Leave empty to auto-detect LAN IP at startup.
    PUBLIC_BASE_URL: str = ""

    # Local File Storage
    UPLOAD_DIR: str = "./uploads"

    # File Settings
    MAX_FILE_SIZE_BYTES: int = 5368709120    # 5 GB
    CHUNK_SIZE_BYTES: int = 5242880          # 5 MB
    SHARE_LINK_EXPIRY_HOURS: int = 72
    UPLOAD_SESSION_TTL_SECONDS: int = 3600

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def get_public_base_url(fallback_port: int = 8000) -> str:
    """
    Return the public base URL for share links.
    Priority:
      1. PUBLIC_BASE_URL from .env / config
      2. Auto-detected LAN IP with the given port
      3. Fallback to http://127.0.0.1:{port}
    """
    if settings.PUBLIC_BASE_URL:
        return settings.PUBLIC_BASE_URL.rstrip("/")

    import socket
    try:
        # Create a UDP socket to determine outbound LAN IP (no data is sent)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        lan_ip = s.getsockname()[0]
        s.close()
        return f"http://{lan_ip}:{fallback_port}"
    except Exception:
        return f"http://127.0.0.1:{fallback_port}"

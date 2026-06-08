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

    # Redis (optional — set REDIS_ENABLED=True to use Redis for upload sessions)
    REDIS_ENABLED: bool = False
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

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

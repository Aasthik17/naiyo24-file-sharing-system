from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.router import api_router
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────────
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode")

    # 1. Create database tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables verified ✓")

        # Create default system user for anonymous frontend uploads
        from app.core.database import AsyncSessionLocal
        from app.models.user import User
        from sqlalchemy import select
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.id == 1))
            system_user = result.scalar_one_or_none()
            if not system_user:
                system_user = User(
                    id=1,
                    email="system@fileshare.local",
                    password="dummy_hash_no_login",
                    is_active=True
                )
                session.add(system_user)
                await session.commit()
                logger.info("System user (id=1) created ✓")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

    # 2. Create local upload directory
    try:
        from app.services.storage_service import ensure_upload_dir
        ensure_upload_dir()
    except Exception as e:
        logger.error(f"Failed to create upload directory: {e}")
        raise

    # 3. Check Redis connection (if enabled)
    if settings.REDIS_ENABLED:
        try:
            from app.services.upload_service import _get_redis
            r = await _get_redis()
            if r:
                logger.info("Redis connection verified ✓")
            else:
                logger.warning("Redis enabled but connection failed — using in-memory fallback")
        except Exception as e:
            logger.warning(f"Redis check failed (will use in-memory fallback): {e}")
    else:
        logger.info("Redis disabled — using in-memory session store")

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    await engine.dispose()
    logger.info("Database connections closed ✓")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# In DEBUG mode: allow all localhost / LAN origins so the Flutter web app
# (served on e.g. http://localhost:52xxx) can reach the backend without CORS
# errors. In production: restrict to the real domain.
_DEBUG_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    # Flutter web dev server uses a random high port — cover the full range
    *[f"http://localhost:{p}" for p in range(3000, 65536)],
    *[f"http://127.0.0.1:{p}" for p in range(3000, 65536)],
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_DEBUG_ORIGINS if settings.DEBUG else ["https://yourdomain.com"],
    allow_origin_regex=(
        # Also allow any LAN IP (192.168.x.x / 10.x / 172.16-31.x) on any port
        r"http://(192\.168|10\.|172\.(1[6-9]|2\d|3[01]))\.\d+\.\d+(:\d+)?$"
    ) if settings.DEBUG else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix="/api")


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}


# ── Public Download Route ─────────────────────────────────────────────────────
from fastapi import Query, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.routes.download import download_file
from typing import Optional

@app.get("/d/{filename}", tags=["Public Download"])
async def public_download(
    filename: str,
    request: Request,
    token: str = Query(..., description="Share token for access"),
    password: Optional[str] = Query(None, description="Password if share is protected"),
    db: AsyncSession = Depends(get_db),
):
    """
    Public-facing endpoint for file downloads.
    The filename in the path is for display purposes (so it shows in browsers/managers).
    The actual file serving is handled securely using the token.
    """
    return await download_file(token=token, request=request, password=password, db=db)

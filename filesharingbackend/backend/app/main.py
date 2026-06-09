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


    # 4. Log public base URL for share links
    from app.core.config import get_public_base_url
    public_url = get_public_base_url()
    logger.info(f"Public base URL for share links: {public_url}")

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://yourdomain.com"],
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

"""
Celery worker configuration.
Only initializes if Redis is enabled (REDIS_ENABLED=True in .env).
"""
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

celery_app = None

if settings.REDIS_ENABLED and settings.CELERY_BROKER_URL:
    try:
        from celery import Celery

        celery_app = Celery(
            "filesharesystem",
            broker=settings.CELERY_BROKER_URL,
            backend=settings.CELERY_RESULT_BACKEND,
            include=["app.workers.tasks"],
        )

        celery_app.conf.update(
            task_serializer="json",
            result_serializer="json",
            accept_content=["json"],
            timezone="Asia/Kolkata",
            enable_utc=True,
            # Auto-retry on failure
            task_acks_late=True,
            task_reject_on_worker_lost=True,
        )

        logger.info("Celery worker configured ✓")

    except Exception as e:
        logger.warning(f"Celery initialization failed (background tasks disabled): {e}")
        celery_app = None
else:
    logger.info("Celery disabled (REDIS_ENABLED=False) — background tasks will not run")

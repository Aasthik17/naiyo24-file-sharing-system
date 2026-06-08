"""
Celery background tasks — production implementations.
- Delete expired share links
- Cleanup incomplete upload sessions

These tasks only run when Celery is enabled (REDIS_ENABLED=True).
"""
from datetime import datetime, timezone

from app.core.config import settings
from app.workers.celery_worker import celery_app
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _get_sync_session():
    """Create a synchronous DB session for Celery tasks."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    sync_db_url = settings.DATABASE_URL.replace("+asyncpg", "+psycopg2")
    sync_engine = create_engine(sync_db_url, pool_pre_ping=True)
    return Session(bind=sync_engine)


# ── Task: Delete Expired Shares ──────────────────────────────────────────────
if celery_app is not None:

    @celery_app.task(
        name="tasks.delete_expired_shares",
        bind=True,
        max_retries=3,
        default_retry_delay=60,
    )
    def delete_expired_shares(self):
        """
        Find all shares whose expiry_time has passed and deactivate them.
        Runs periodically via Celery Beat.
        """
        from sqlalchemy import select
        from app.models.share import Share

        logger.info("Running delete_expired_shares task...")
        now = datetime.now(timezone.utc)

        try:
            with _get_sync_session() as session:
                result = session.execute(
                    select(Share).where(
                        Share.is_active == True,
                        Share.expiry_time != None,
                        Share.expiry_time < now,
                    )
                )
                expired_shares = result.scalars().all()

                if not expired_shares:
                    logger.info("No expired shares found")
                    return {"status": "ok", "deactivated": 0}

                count = 0
                for share in expired_shares:
                    share.is_active = False
                    count += 1

                session.commit()
                logger.info(f"Deactivated {count} expired share links")
                return {"status": "ok", "deactivated": count}

        except Exception as exc:
            logger.error(f"delete_expired_shares failed: {exc}")
            raise self.retry(exc=exc)


    # ── Task: Cleanup Incomplete Uploads ─────────────────────────────────────
    @celery_app.task(
        name="tasks.cleanup_incomplete_uploads",
        bind=True,
        max_retries=3,
        default_retry_delay=60,
    )
    def cleanup_incomplete_uploads(self):
        """
        Scan Redis for upload sessions that have exceeded TTL
        and clean up their chunk files from local storage.
        """
        import redis as sync_redis
        from app.services.storage_service import delete_upload_session_files

        logger.info("Running cleanup_incomplete_uploads task...")

        try:
            r = sync_redis.from_url(settings.REDIS_URL, decode_responses=True)

            cursor = 0
            cleaned = 0

            while True:
                cursor, keys = r.scan(cursor, match="upload_session:*", count=100)

                for key in keys:
                    session = r.hgetall(key)
                    if not session:
                        continue

                    status_val = session.get("status", "")
                    if status_val == "in_progress":
                        ttl = r.ttl(key)
                        if ttl is not None and 0 < ttl < 60:
                            user_id = session.get("user_id")
                            upload_id = session.get("upload_id")
                            if user_id and upload_id:
                                delete_upload_session_files(int(user_id), upload_id)
                                r.delete(key)
                                cleaned += 1
                                logger.info(
                                    f"Cleaned up stale upload session: {upload_id}"
                                )

                if cursor == 0:
                    break

            logger.info(f"Cleanup complete: {cleaned} stale uploads removed")
            return {"status": "ok", "cleaned": cleaned}

        except Exception as exc:
            logger.error(f"cleanup_incomplete_uploads failed: {exc}")
            raise self.retry(exc=exc)


    # ── Celery Beat Schedule ─────────────────────────────────────────────────
    celery_app.conf.beat_schedule = {
        "delete-expired-shares-every-hour": {
            "task": "tasks.delete_expired_shares",
            "schedule": 3600.0,
        },
        "cleanup-incomplete-uploads-every-30-min": {
            "task": "tasks.cleanup_incomplete_uploads",
            "schedule": 1800.0,
        },
    }

else:
    logger.info("Celery tasks not registered (Celery is disabled)")

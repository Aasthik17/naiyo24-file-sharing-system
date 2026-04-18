from celery import Celery
from app.core.config import settings

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

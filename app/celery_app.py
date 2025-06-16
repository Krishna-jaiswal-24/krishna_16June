from celery import Celery
from app.settings import Settings

settings = Settings()

celery_app = Celery(
    "store_monitor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.tasks.report_tasks']  # Include our tasks module
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
) 
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "forstek",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks", "app.tasks.scraping", "app.tasks.ai_tasks"]
)

celery_app.conf.timezone = "Africa/Tunis"
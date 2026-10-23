from celery import Celery
from app.config import REDIS_URL

celery_app = Celery("dobox", broker=REDIS_URL, include=["app.tasks.achievements"])
celery_app.conf.task_acks_late = True
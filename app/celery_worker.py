from celery import Celery

from app.config import Config

def make_celery(app_name=__name__):
    celery = Celery(
        app_name,
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
        include=["app.tasks"]
    )

    return celery

celery = make_celery()
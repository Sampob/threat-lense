from app import create_app
from app.config import Config

from celery import Celery

def make_celery(app) -> Celery:
    """
    Create celery instance.

    :param app: Flask application instance

    :return: Created celery
    """
    celery = Celery(
        app.import_name,
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
        include=["app.tasks"]
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

app = create_app()
celery = make_celery(app)
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
        backend=Config.result_backend,
        include=["app.tasks"]
    )
    celery.conf.update(app.config)

    celery.conf.broker_connection_retry_on_startup = True

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

app = create_app()
celery = make_celery(app)
from celery import Celery
from app.factory import create_app
from app.settings import Settings

flask_app = create_app()

def make_celery(app):
    celery = Celery(app.import_name)
    celery.conf.update(Settings.CELERY_CONFIG)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    Settings.setup_celery_logging()
    return celery

celery = make_celery(flask_app)
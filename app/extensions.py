from authlib.integrations.flask_client import OAuth
from celery import Celery
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth()
migrate = Migrate()
mail = Mail()
celery = Celery(__name__)


def make_celery(app):
    extra_config = app.config.get("CELERY_CONFIG") or {}
    celery.conf.update(extra_config)

    broker_url = app.config.get("CELERY_BROKER_URL") or celery.conf.get("broker_url")
    result_backend = app.config.get("CELERY_RESULT_BACKEND") or celery.conf.get(
        "result_backend"
    )
    celery.conf.update(
        broker_url=broker_url,
        result_backend=result_backend,
    )

    # Ensure tasks are registered for both worker and beat.
    celery.autodiscover_tasks(["app"])

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    oauth.init_app(app)
    mail.init_app(app)

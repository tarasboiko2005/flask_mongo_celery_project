import os
from celery import Celery
from celery.schedules import crontab
from app.factory import create_app

flask_app = create_app()

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=os.getenv("REDIS_URL"),
        backend=os.getenv("REDIS_URL"),
    )
    celery.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"]
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = make_celery(flask_app)

celery.conf.beat_schedule = {
    "parse-page-every-morning": {
        "task": "tasks.parse_page",
        "schedule": crontab(hour=7, minute=0),
        "args": (
            os.getenv("DAILY_JOB_ID", "job_daily"),
            os.getenv("PARSER_URL", "https://www.python.org"),
            int(os.getenv("PARSER_LIMIT", "5")),
        ),
    },
}
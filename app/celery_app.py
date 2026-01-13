import os
from celery import Celery
from flask import Flask

def make_celery(app: Flask):
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
    return celery
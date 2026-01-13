import os
from flasgger import Swagger
from flask import Flask
from pymongo import MongoClient
from celery import Celery
from .tasks import register_task

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

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.config["FILE_OUTPUT_DIR"] = os.getenv("FILE_OUTPUT_DIR", "./output")

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/apispec_1.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        "title": "Image & Parsing Job API"
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Image & Parsing Job API",
            "version": "1.0.0"
        },
        "basePath": "/api",
        "schemes": ["http"],
        "tags": [
            {
                "name": "Jobs",
                "description": "Job endpoints"
            }
        ]
    }

    Swagger(app, config=swagger_config, template=swagger_template)

    client = MongoClient(app.config["MONGO_URI"])
    app.mongo_db = client.get_default_database()
    app.jobs = app.mongo_db["jobs"]

    os.makedirs(app.config["FILE_OUTPUT_DIR"], exist_ok=True)

    app.celery_app = make_celery(app)
    register_task(app.celery_app)

    from .routes import blueprints
    for bp in blueprints:
        app.register_blueprint(bp, url_prefix="/api")

    return app
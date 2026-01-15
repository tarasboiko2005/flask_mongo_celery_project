import os
import logging
from logging.handlers import RotatingFileHandler
from celery.schedules import crontab

class Settings:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    PREFERRED_URL_SCHEME = "http"

    # Mongo
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB_NAME = "flask_jobs"
    MONGO_COLLECTION_NAME = "jobs"

    # Files
    FILE_OUTPUT_DIR = os.getenv("FILE_OUTPUT_DIR", "./output")

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_OAUTH_CONFIG = {
        "name": "google",
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
        "client_kwargs": {"scope": "openid email profile"},
    }

    # Swagger
    SWAGGER_CONFIG = {
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
        "title": "Image & Parsing Job API",
        "uiversion": 3
    }

    SWAGGER_TEMPLATE = {
        "swagger": "2.0",
        "info": {"title": "Image & Parsing Job API", "version": "1.0.0"},
        "basePath": "/api",
        "schemes": ["http"],
        "tags": [{"name": "Jobs", "description": "Job endpoints"}]
    }

    @staticmethod
    def setup_logging(app):
        handler = RotatingFileHandler("debug.log", maxBytes=1000000, backupCount=3)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Celery
    DAILY_JOB_ID = os.getenv("DAILY_JOB_ID", "job_daily")
    PARSER_URL = os.getenv("PARSER_URL", "https://www.python.org")
    PARSER_LIMIT = int(os.getenv("PARSER_LIMIT", "5"))

    CELERY_CONFIG = {
        "broker_url": REDIS_URL,
        "result_backend": REDIS_URL,
        "task_serializer": "json",
        "result_serializer": "json",
        "accept_content": ["json"],
        "beat_schedule": {
            "parse-page-every-morning": {
                "task": "tasks.parse_page",
                "schedule": crontab(hour=7, minute=0),
                "args": (DAILY_JOB_ID, PARSER_URL, PARSER_LIMIT),
            },
        },
    }

    @staticmethod
    def setup_celery_logging():
        handler = RotatingFileHandler("debug.log", maxBytes=1000000, backupCount=3)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        handler.setFormatter(formatter)

        logger = logging.getLogger("celery")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
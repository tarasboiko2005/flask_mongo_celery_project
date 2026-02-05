import logging
import os
from logging.handlers import RotatingFileHandler

from celery.schedules import crontab


class Settings:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    PREFERRED_URL_SCHEME = "https"

    # Mongo
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB_NAME = "flask_jobs"
    MONGO_COLLECTION_NAME = "jobs"

    # Files
    FILE_OUTPUT_DIR = os.getenv("FILE_OUTPUT_DIR", "./output")

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # BASE_URL for OAuth redirect
    BASE_URL = os.getenv(
        "BASE_URL", "https://flaskmongoceleryproject-production-2064.up.railway.app"
    )

    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_OAUTH_CONFIG = {
        "name": "google",
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
        "client_kwargs": {"scope": "openid email profile"},
        "redirect_uri": f"{BASE_URL}/auth/authorize",
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
        "specs_route": "/api/docs/",
        "title": "Image & Parsing Job API",
        "uiversion": 3,
    }

    SWAGGER_TEMPLATE = {
        "swagger": "2.0",
        "info": {"title": "Image & Parsing Job API", "version": "1.0.0"},
        "basePath": "/api",
        "schemes": ["https"],
        "tags": [{"name": "Jobs", "description": "Job endpoints"}],
    }

    @staticmethod
    def setup_logging(app):
        handler = RotatingFileHandler("debug.log", maxBytes=1000000, backupCount=3)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

    # Celery
    DAILY_JOB_ID = os.getenv("DAILY_JOB_ID", "job_daily")
    PARSER_URL = os.getenv("PARSER_URL", "https://www.python.org")
    PARSER_LIMIT = int(os.getenv("PARSER_LIMIT", "5"))
    DAILY_JOB_USER_EMAIL = os.getenv(
        "DAILY_JOB_USER_EMAIL", os.getenv("MAIL_DEFAULT_SENDER", "test@example.com")
    )

    CELERY_CONFIG = {
        "task_serializer": "json",
        "result_serializer": "json",
        "accept_content": ["json"],
        "beat_schedule": {
            "parse-page-every-morning": {
                "task": "tasks.parse_page",
                "schedule": crontab(hour=7, minute=0),
                "args": (DAILY_JOB_ID, PARSER_URL, DAILY_JOB_USER_EMAIL, PARSER_LIMIT),
            },
        },
    }

    @staticmethod
    def setup_celery_logging():
        handler = RotatingFileHandler("debug.log", maxBytes=1000000, backupCount=3)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)

        logger = logging.getLogger("celery")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379/0"
    )

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "false").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

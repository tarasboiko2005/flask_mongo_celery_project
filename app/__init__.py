import os
from flasgger import Swagger
from flask import Flask
from pymongo import MongoClient
from flask_login import current_user, LoginManager
from app.tasks import register_task
from .celery_app import make_celery
from app.schemas import JobStatusResponse, ParseJobRequest, ImageUploadRequest, ProcessedFile
from app.db import db
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app.models import User, Job

load_dotenv()

login_manager = LoginManager()
oauth = OAuth()

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False
    app.config["PREFERRED_URL_SCHEME"] = "http"

    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.config["FILE_OUTPUT_DIR"] = os.getenv("FILE_OUTPUT_DIR", "./output")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

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
        "info": {"title": "Image & Parsing Job API", "version": "1.0.0"},
        "basePath": "/api",
        "schemes": ["http"],
        "tags": [{"name": "Jobs", "description": "Job endpoints"}]
    }
    definitions = {
        "JobStatus": JobStatusResponse.model_json_schema(ref_template="#/definitions/{model}"),
        "ParseJobRequest": ParseJobRequest.model_json_schema(ref_template="#/definitions/{model}"),
        "ImageUploadRequest": ImageUploadRequest.model_json_schema(ref_template="#/definitions/{model}"),
        "ProcessedFile": ProcessedFile.model_json_schema(ref_template="#/definitions/{model}")
    }
    Swagger(app, config=swagger_config, template={**swagger_template, "definitions": definitions})

    client = MongoClient(app.config["MONGO_URI"])
    app.mongo_db = client["flask_jobs"]
    app.jobs = app.mongo_db["jobs"]

    os.makedirs(app.config["FILE_OUTPUT_DIR"], exist_ok=True)
    app.celery_app = make_celery(app)
    register_task(app.celery_app)

    login_manager.init_app(app)
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    from .routes import blueprints
    for bp in blueprints:
        app.register_blueprint(bp, url_prefix="/api")

    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return f"Welcome, {current_user.name} ({current_user.email})"
        return "Hello, please log in."

    admin = Admin(app, name="Control Panel")
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Job, db.session))

    with app.app_context():
        db.create_all()

    return app

flask_app = create_app()
celery_app = flask_app.celery_app
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
from app.settings import Settings
from flask_migrate import Migrate

load_dotenv()

login_manager = LoginManager()
oauth = OAuth()

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Settings)
    db.init_app(app)
    migrate.init_app(app, db)

    definitions = {
        "JobStatus": JobStatusResponse.model_json_schema(ref_template="#/definitions/{model}"),
        "ParseJobRequest": ParseJobRequest.model_json_schema(ref_template="#/definitions/{model}"),
        "ImageUploadRequest": ImageUploadRequest.model_json_schema(ref_template="#/definitions/{model}"),
        "ProcessedFile": ProcessedFile.model_json_schema(ref_template="#/definitions/{model}")
    }
    Swagger(app, config=Settings.SWAGGER_CONFIG,
            template={**Settings.SWAGGER_TEMPLATE, "definitions": definitions})

    client = MongoClient(app.config["MONGO_URI"])
    app.mongo_db = client[Settings.MONGO_DB_NAME]
    app.jobs = app.mongo_db[Settings.MONGO_COLLECTION_NAME]

    os.makedirs(app.config["FILE_OUTPUT_DIR"], exist_ok=True)
    app.celery_app = make_celery(app)
    register_task(app.celery_app)

    login_manager.init_app(app)
    oauth.init_app(app)
    oauth.register(**Settings.GOOGLE_OAUTH_CONFIG)

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

    Settings.setup_logging(app)

    return app

flask_app = create_app()
celery_app = flask_app.celery_app
import os

from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask, jsonify, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_cors import CORS
from flask_login import current_user
from pymongo import MongoClient

from app.extensions import (
    celery,
    db,
    login_manager,
    mail,
    make_celery,
    migrate,
    oauth,
)
from app.mcp.agent import run_agent
from app.models import Job, User
from app.rag.rag_pipeline import query_history
from app.routes.agent import agent_bp
from app.routes.email import email_bp
from app.routes.health import health_bp
from app.schemas import (
    ImageUploadRequest,
    JobStatusResponse,
    ParseJobRequest,
    ProcessedFile,
    SendJobReportRequest,
)
from app.settings import Settings


def create_app():
    load_dotenv()
    app = Flask(__name__)

    app.config.from_object(Settings)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret"),
        SQLALCHEMY_DATABASE_URI=os.getenv("SQLALCHEMY_DATABASE_URI"),
        MONGO_URI=os.getenv("MONGO_URI"),
        CELERY_BROKER_URL=os.getenv("CELERY_BROKER_URL"),
        CELERY_RESULT_BACKEND=os.getenv("CELERY_RESULT_BACKEND"),
        MAIL_SERVER=os.getenv("MAIL_SERVER"),
        MAIL_PORT=int(os.getenv("MAIL_PORT", 25)),
        MAIL_USE_TLS=os.getenv("MAIL_USE_TLS") == "True",
        MAIL_USE_SSL=os.getenv("MAIL_USE_SSL") == "True",
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER", "test@example.com"),
        FILE_OUTPUT_DIR=os.getenv("FILE_OUTPUT_DIR", "/app/output"),
    )

    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    oauth.init_app(app)
    oauth.register(**Settings.GOOGLE_OAUTH_CONFIG)
    CORS(app)

    make_celery(app)
    app.celery = celery

    app.register_blueprint(email_bp, url_prefix="/api")
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(agent_bp, url_prefix="/api")

    from .routes import blueprints

    for bp in blueprints:
        app.register_blueprint(bp, url_prefix="/api")

    from .routes.auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    definitions = {
        "JobStatus": JobStatusResponse.model_json_schema(
            ref_template="#/definitions/{model}"
        ),
        "ParseJobRequest": ParseJobRequest.model_json_schema(
            ref_template="#/definitions/{model}"
        ),
        "ImageUploadRequest": ImageUploadRequest.model_json_schema(
            ref_template="#/definitions/{model}"
        ),
        "ProcessedFile": ProcessedFile.model_json_schema(
            ref_template="#/definitions/{model}"
        ),
        "SendJobReportRequest": SendJobReportRequest.model_json_schema(
            ref_template="#/definitions/{model}"
        ),
    }
    Swagger(
        app,
        config=Settings.SWAGGER_CONFIG,
        template={**Settings.SWAGGER_TEMPLATE, "definitions": definitions},
    )

    client = MongoClient(app.config["MONGO_URI"])
    app.mongo_db = client[Settings.MONGO_DB_NAME]
    app.jobs = app.mongo_db[Settings.MONGO_COLLECTION_NAME]

    os.makedirs(app.config["FILE_OUTPUT_DIR"], exist_ok=True)

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return f"Welcome, {current_user.name} ({current_user.email})"
        return "Hello, please log in."

    @app.route("/rag", methods=["POST"])
    def rag_query():
        question = request.json.get("question")
        answer = query_history(question)
        return jsonify({"answer": answer})

    @app.route("/agent", methods=["POST"])
    def agent_query():
        data = request.get_json(silent=True) or {}
        query = data.get("query")
        debug = bool(data.get("debug", False))
        if not query:
            return jsonify({"error": "Missing 'query' field"}), 400
        result = run_agent(query, debug=debug)
        return jsonify(result)

    admin = Admin(app, name="Control Panel")
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Job, db.session))

    with app.app_context():
        db.create_all(checkfirst=True)

    Settings.setup_logging(app)

    return app

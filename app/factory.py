import os
from flasgger import Swagger
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from .routes import blueprints

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.config["FILE_OUTPUT_DIR"] = os.getenv("FILE_OUTPUT_DIR", "./output")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    Swagger(app)

    client = MongoClient(app.config["MONGO_URI"])
    app.mongo_db = client["flask_jobs"]
    app.jobs = app.mongo_db["jobs"]

    os.makedirs(app.config["FILE_OUTPUT_DIR"], exist_ok=True)

    for bp in blueprints:
        app.register_blueprint(bp, url_prefix="/api")

    with app.app_context():
        db.create_all()

    return app
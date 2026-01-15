import os
from flask import Flask
from flasgger import Swagger
from pymongo import MongoClient
from .settings import Settings
from .routes import blueprints
from .db import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Settings)

    db.init_app(app)

    Swagger(app, config=Settings.SWAGGER_CONFIG,
            template={**Settings.SWAGGER_TEMPLATE})

    client = MongoClient(app.config["MONGO_URI"])
    app.mongo_db = client[Settings.MONGO_DB_NAME]
    app.jobs = app.mongo_db[Settings.MONGO_COLLECTION_NAME]

    os.makedirs(app.config["FILE_OUTPUT_DIR"], exist_ok=True)

    for bp in blueprints:
        app.register_blueprint(bp, url_prefix="/api")

    return app
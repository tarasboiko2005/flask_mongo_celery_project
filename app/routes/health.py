from flask import Blueprint, jsonify
from app.db import db
import redis
from pymongo import MongoClient
from app.settings import Settings
from sqlalchemy import text

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint
    ---
    responses:
      200:
        description: Service health status
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
            checks:
              type: object
              properties:
                db:
                  type: string
                  example: ok
                redis:
                  type: string
                  example: ok
                mongo:
                  type: string
                  example: ok
    """
    checks = {}

    try:
        db.session.execute(text("SELECT 1"))
        checks["db"] = "ok"
    except Exception as e:
        checks["db"] = f"error: {str(e)}"

    try:
        r = redis.Redis(host=Settings.REDIS_HOST, port=Settings.REDIS_PORT)
        r.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"

    try:
        client = MongoClient(Settings.MONGO_URI)
        client.admin.command("ping")
        checks["mongo"] = "ok"
    except Exception as e:
        checks["mongo"] = f"error: {str(e)}"

    return jsonify({"status": "ok", "checks": checks}), 200
from flask import Blueprint, request, jsonify, current_app
import uuid
from datetime import datetime

bp = Blueprint("parse_jobs", __name__)

@bp.route("/jobs/parse", methods=["POST"])
def parse_job():
    """
    Parse a webpage for images
    ---
    tags:
      - Jobs
    consumes:
      - multipart/form-data
    parameters:
      - name: url
        in: formData
        type: string
        required: true
        description: Target webpage URL to parse for images
      - name: limit
        in: formData
        type: integer
        required: false
        description: Max number of images to process (default 5)
    responses:
      202:
        description: Parse job created
    """
    url = request.form["url"]

    try:
        limit = int(request.form.get("limit", 5))
    except ValueError:
        limit = 5

    job_id = str(uuid.uuid4())
    doc = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "url": url,
        "limit": limit
    }
    current_app.jobs.insert_one(doc)

    current_app.celery_app.send_task("tasks.parse_page", args=[job_id, url, limit])

    return jsonify({"job_id": job_id, "status": "queued"}), 202
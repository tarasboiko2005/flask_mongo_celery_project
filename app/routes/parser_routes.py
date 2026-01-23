from flask import Blueprint, request, jsonify, current_app
import uuid
from datetime import datetime
from pydantic import ValidationError
from app.schemas import ParseJobRequest
from app.tasks.parser_tasks import parse_page

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
    try:
        data = ParseJobRequest(
            url=request.form.get("url"),
            limit=request.form.get("limit")
        )
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    job_id = str(uuid.uuid4())
    doc = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "url": str(data.url),
        "limit": data.limit
    }
    current_app.jobs.insert_one(doc)
    parse_page.delay(job_id, str(data.url), data.limit)
    return jsonify({"job_id": job_id, "status": "queued"}), 202
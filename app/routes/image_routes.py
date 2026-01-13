from flask import Blueprint, request, jsonify, current_app
import os, uuid
from datetime import datetime

bp = Blueprint("image_jobs", __name__)

@bp.route("/jobs/image", methods=["POST"])
def upload_image():
    """
    Upload image for processing (grayscale)
    ---
    tags:
      - Jobs
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
    responses:
      202:
        description: Image job created
    """
    file = request.files["file"]
    filename = file.filename
    output_dir = os.getenv("FILE_OUTPUT_DIR", "./output")
    filepath = os.path.join(output_dir, filename)
    file.save(filepath)

    job_id = str(uuid.uuid4())
    doc = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "filename": filename,
        "file_path": filepath,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    current_app.jobs.insert_one(doc)
    current_app.celery_app.send_task("tasks.process_image", args=[job_id, filename, filepath])

    return jsonify({"job_id": job_id, "status": "queued"}), 202
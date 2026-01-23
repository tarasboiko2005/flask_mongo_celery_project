from flask import Blueprint, request, jsonify, current_app
import os, uuid
from datetime import datetime
from app.schemas import ImageUploadRequest
from pydantic import ValidationError
from app.tasks.image_tasks import process_image

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
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "file_required"}), 400

    try:
        data = ImageUploadRequest(filename=file.filename)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    output_dir = os.getenv("FILE_OUTPUT_DIR", "./output")
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, data.filename)
    file.save(filepath)

    job_id = str(uuid.uuid4())
    doc = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "filename": data.filename,
        "file_path": filepath,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    current_app.jobs.insert_one(doc)
    process_image.delay(job_id, data.filename, filepath)

    return jsonify({"job_id": job_id, "status": "queued"}), 202
import uuid, os
from datetime import datetime
from flask import Blueprint, current_app, jsonify, send_file, request
bp = Blueprint("api", __name__)

@bp.route("/jobs/image", methods=["POST"])
def upload_image():
    """
    Upload image for processing
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

    return jsonify({"job_id": job_id, "status": "queued", "progress": 0}), 202

@bp.route("/jobs/<job_id>", methods=["GET"])
def job_status(job_id):
    """
    Get job status
    ---
    tags:
      - Jobs
    parameters:
      - name: job_id
        in: path
        required: true
        type: string
    responses:
      200:
        description: Job status
        schema:
          type: object
          properties:
            job_id:
              type: string
            status:
              type: string
              enum: [queued, processing, ready]
            progress:
              type: integer
            created_at:
              type: string
            updated_at:
              type: string
      404:
        description: Job not found
    """
    job = current_app.jobs.find_one({"job_id": job_id}, {"_id": 0})
    if not job:
        return jsonify({"error": "not_found"}), 404
    return jsonify(job)

@bp.route("/jobs/<job_id>/download", methods=["GET"])
def job_download(job_id):
    """
    Download job result
    ---
    tags:
      - Jobs
    parameters:
      - name: job_id
        in: path
        required: true
        type: string
    responses:
      200:
        description: File ready for download
        examples:
          text/plain:
            "This would be the content of the generated file."
      409:
        description: Job not ready
        examples:
          application/json:
            {
              "error": "not_ready"
            }
      404:
        description: Job not found
        examples:
          application/json:
            {
              "error": "not_found"
            }
    """
    job = current_app.jobs.find_one({"job_id": job_id})
    if not job:
        return jsonify({"error": "not_found"}), 404
    if job["status"] != "ready":
        return jsonify({"error": "not_ready"}), 409
    return send_file(
        job["file_path"],
        as_attachment=True,
        download_name=job.get("filename", f"{job_id}.txt")
    )
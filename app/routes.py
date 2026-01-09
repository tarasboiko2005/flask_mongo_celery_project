import uuid
from datetime import datetime
from flask import Blueprint, current_app, jsonify, send_file, request
bp = Blueprint("api", __name__)

@bp.route("/jobs", methods=["POST"])
def create_job():
    """
    Create a new job
    ---
    tags:
      - Jobs
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            filename:
              type: string
              description: Name of the file to generate
            priority:
              type: string
              enum: [low, medium, high]
              default: low
              description: Priority of the job
    responses:
      202:
        description: Job created
        examples:
          application/json:
            {
              "job_id": "1",
              "status": "queued",
              "progress": 0
            }
    """
    data = request.get_json() or {}
    filename = data.get("filename", "default.txt")
    priority = data.get("priority", "low")

    job_id = str(uuid.uuid4())
    doc = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "priority": priority,
        "filename": filename,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    current_app.jobs.insert_one(doc)
    current_app.celery_app.send_task("tasks.generate_file", args=[job_id, filename])
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
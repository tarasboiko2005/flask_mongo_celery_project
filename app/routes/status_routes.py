from flask import Blueprint, jsonify, current_app, request, send_file
from pydantic import ValidationError
from app.schemas import JobStatusResponse, ProcessedFile
from email.utils import parsedate_to_datetime

bp = Blueprint("status_jobs", __name__)

def normalize_datetime_fields(job):
    for field in ["created_at", "updated_at"]:
        if field in job and isinstance(job[field], str):
            try:
                parsed = parsedate_to_datetime(job[field])
                job[field] = parsed.isoformat()
            except Exception:
                pass

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
          $ref: '#/definitions/JobStatus'
      404:
        description: Job not found
      400:
        description: Invalid job format
    """
    job = current_app.jobs.find_one({"job_id": job_id}, {"_id": 0})
    if not job:
        return jsonify({"error": "not_found"}), 404

    normalize_datetime_fields(job)

    if "processed_files" in job and job["processed_files"]:
        job["processed_files"] = [ProcessedFile(**f).dict() for f in job["processed_files"]]

    try:
        data = JobStatusResponse(**job)
    except ValidationError as e:
        return jsonify({"error": e.errors(), "raw": job}), 400

    return jsonify(data.model_dump(mode="json"))

@bp.route("/jobs/<job_id>/download", methods=["GET"])
def job_download(job_id):
    """
    Download processed image(s)
    ---
    tags:
      - Jobs
    parameters:
      - name: job_id
        in: path
        required: true
        type: string
      - name: index
        in: query
        required: false
        type: integer
        description: Index of processed image (default 0, only for multi-file jobs)
    responses:
      200:
        description: File ready for download
      409:
        description: Job not ready or no file
      404:
        description: Job not found
    """
    job = current_app.jobs.find_one({"job_id": job_id})
    if not job:
        return jsonify({"error": "not_found"}), 404
    if job.get("status") != "ready":
        return jsonify({"error": "not_ready"}), 409

    files = job.get("processed_files")
    if files:
        index = int(request.args.get("index", 0))
        if index >= len(files):
            return jsonify({"error": "invalid_index"}), 409
        file_info = files[index]
        return send_file(file_info["file_path"], as_attachment=True, download_name=file_info["filename"])

    if "file_path" in job and "filename" in job:
        return send_file(job["file_path"], as_attachment=True, download_name=job["filename"])

    return jsonify({"error": "no_file"}), 409
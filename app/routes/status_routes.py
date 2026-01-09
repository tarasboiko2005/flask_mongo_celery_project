from flask import request
from flask import Blueprint, jsonify, current_app, send_file

bp = Blueprint("status_jobs", __name__)

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
    Download processed image by index
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
        description: Index of processed image (default 0)
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
    if job["status"] != "ready":
        return jsonify({"error": "not_ready"}), 409

    index = int(request.args.get("index", 0))
    files = job.get("processed_files", [])

    if index >= len(files):
        return jsonify({"error": "invalid_index"}), 409

    file_info = files[index]
    return send_file(
        file_info["file_path"],
        as_attachment=True,
        download_name=file_info["filename"]
    )
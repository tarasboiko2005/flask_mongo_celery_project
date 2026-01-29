from flask import Blueprint, request, jsonify
from app.tasks.email_tasks import send_job_report

email_bp = Blueprint("email", __name__)

@email_bp.route("/send_job_report", methods=["POST"])
def send_job_report_endpoint():
    """
    Send job report email
    ---
    tags:
      - Email
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: string
              example: "42"
            job_id:
              type: string
              example: "123"
    responses:
      202:
        description: Email task queued
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Email task queued"
    """
    data = request.get_json()
    job_id = data.get("job_id")
    user_id = data.get("user_id")
    send_job_report.delay(job_id, user_id)
    return jsonify({"message": "Email task queued"}), 202
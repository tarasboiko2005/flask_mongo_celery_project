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
            user_email:
              type: string
              example: "tarasboiko2005@gmail.com"
            job_id:
              type: string
              example: "123"
            status:
              type: string
              example: "completed"
            details:
              type: string
              example: "Everything went well."
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
    user_email = data.get("user_email")
    job_id = data.get("job_id")
    status = data.get("status")
    details = data.get("details")
    send_job_report.delay(user_email, job_id, status, details)
    return jsonify({"message": "Email task queued"}), 202
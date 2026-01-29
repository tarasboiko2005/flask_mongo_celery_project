from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.tasks.email_tasks import send_job_report

email_bp = Blueprint("email", __name__)

@email_bp.route("/send_job_report", methods=["POST"])
@login_required
def send_job_report_endpoint():
    """
    Sending a report to the logged-in user's email.
    ---
    tags:
      - Email
    responses:
      202:
        description: Email task queued
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Email task queued for user@example.com"
      400:
        description: Bad request (There is no user email)
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "User email not available"
      401:
        description: Unauthorized (user is not logged in)
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Login required"
    """
    user_email = getattr(current_user, "email", None)
    if not user_email:
        return jsonify({"error": "User email not available"}), 400
    job_id = "123"
    status = "completed"
    details = "Everything went well"
    send_job_report.delay(user_email, job_id, status, details)
    return jsonify({"message": f"Email task queued for {user_email}"}), 202
import uuid
import random
import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash
from pymongo import MongoClient
from app.tasks.email_tasks import send_job_report

security_bp = Blueprint("security", __name__)

def generate_otp(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

@security_bp.route("/request_otp", methods=["POST"])
def request_otp():
    """
    Request OTP
    ---
    tags:
      - Security
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: user@example.com
    responses:
      200:
        description: OTP sent successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: OTP sent
      400:
        description: Email required
    """
    data = request.get_json() or {}
    user_email = data.get("email")
    if not user_email:
        return jsonify({"error": "Email required"}), 400

    client = MongoClient(current_app.config["MONGO_URI"])
    db = client.get_default_database()
    otp_codes = db["otp_codes"]

    code = generate_otp()
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)

    otp_codes.insert_one({
        "email": user_email,
        "code": code,
        "expires_at": expires_at
    })

    send_job_report.delay(
        user_email,
        job_id="otp",
        status="ready",
        details=f"Your OTP code is {code}. It will expire in 5 minutes."
    )

    return jsonify({"message": "OTP sent"}), 200

@security_bp.route("/verify_otp", methods=["POST"])
def verify_otp():
    """
    Verify OTP
    ---
    tags:
      - Security
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: user@example.com
            code:
              type: string
              example: "123456"
    responses:
      200:
        description: OTP verified successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: OTP verified
      400:
        description: Invalid or expired OTP
    """
    data = request.get_json() or {}
    user_email = data.get("email")
    code = data.get("code")

    client = MongoClient(current_app.config["MONGO_URI"])
    db = client.get_default_database()
    otp_codes = db["otp_codes"]

    record = otp_codes.find_one({"email": user_email, "code": code})
    if not record:
        return jsonify({"error": "Invalid code"}), 400

    if record["expires_at"] < datetime.datetime.utcnow():
        return jsonify({"error": "Code expired"}), 400

    return jsonify({"message": "OTP verified"}), 200

@security_bp.route("/request_reset_password", methods=["POST"])
def request_reset_password():
    """
    Request Reset Password
    ---
    tags:
      - Security
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: user@example.com
    responses:
      200:
        description: Reset link sent successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Reset link sent
      400:
        description: Email required
    """
    data = request.get_json() or {}
    user_email = data.get("email")
    if not user_email:
        return jsonify({"error": "Email required"}), 400

    client = MongoClient(current_app.config["MONGO_URI"])
    db = client.get_default_database()
    reset_tokens = db["reset_tokens"]

    token = str(uuid.uuid4())
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    reset_tokens.insert_one({
        "email": user_email,
        "token": token,
        "expires_at": expires_at
    })

    reset_link = f"http://localhost:8000/api/reset?token={token}"
    send_job_report.delay(
        user_email,
        job_id="reset",
        status="ready",
        details=f"Click the following link to reset your password: {reset_link}"
    )

    return jsonify({"message": "Reset link sent"}), 200

@security_bp.route("/reset_password", methods=["POST"])
def reset_password():
    """
    Reset Password
    ---
    tags:
      - Security
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            token:
              type: string
              example: 123e4567-e89b-12d3-a456-426614174000
            new_password:
              type: string
              example: MyNewSecurePassword123
    responses:
      200:
        description: Password updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Password updated
      400:
        description: Invalid or expired token
    """
    data = request.get_json() or {}
    token = data.get("token")
    new_password = data.get("new_password")

    client = MongoClient(current_app.config["MONGO_URI"])
    db = client.get_default_database()
    reset_tokens = db["reset_tokens"]
    users = db["users"]

    record = reset_tokens.find_one({"token": token})
    if not record:
        return jsonify({"error": "Invalid token"}), 400

    if record["expires_at"] < datetime.datetime.utcnow():
        return jsonify({"error": "Token expired"}), 400

    hashed_password = generate_password_hash(new_password)
    users.update_one({"email": record["email"]}, {"$set": {"password": hashed_password}})
    reset_tokens.delete_one({"token": token})

    return jsonify({"message": "Password updated"}), 200

@security_bp.route("/reset", methods=["GET"])
def reset_page():
    """
    Reset Page
    ---
    tags:
      - Security
    parameters:
      - in: query
        name: token
        required: true
        type: string
        description: Reset token
    responses:
      200:
        description: HTML page with token
    """
    token = request.args.get("token")
    if not token:
        return "Token is missing", 400

    return f"""
    <html>
      <head><title>Password Reset</title></head>
      <body>
        <h2>Password Reset</h2>
        <p>Your token is:</p>
        <code>{token}</code>
        <p>Copy this token and use it in Swagger UI or Postman to reset your password.</p>
      </body>
    </html>
    """
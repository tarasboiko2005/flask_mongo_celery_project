from flask import Blueprint, request, jsonify, current_app
import os, uuid
from datetime import datetime
from flask_login import current_user
from app.mcp.agent import run_agent
from app.tasks.parser_tasks import parse_page
from app.tasks.image_tasks import process_image

agent_bp = Blueprint("agent", __name__)

@agent_bp.route("/agent", methods=["POST"])
def post_agent():
    """
    Run agent with query (text/URL) or image
    ---
    tags:
      - Agent
    consumes:
      - application/json
      - multipart/form-data
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            query:
              type: string
              description: Text query or URL
      - name: file
        in: formData
        type: file
        required: false
        description: Image file to convert
    responses:
      200:
        description: Agent response
      400:
        description: Missing input
      500:
        description: Internal error
    """

    if "file" in request.files:
        file = request.files["file"]
        if not file:
            return jsonify({"error": "file_required"}), 400

        filename = file.filename
        output_dir = os.getenv("FILE_OUTPUT_DIR", "./output")
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        file.save(filepath)
        job_id = f"agent-image-{uuid.uuid4().hex}"
        current_app.jobs.insert_one({
            "job_id": job_id,
            "status": "queued",
            "progress": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "filename": filename,
            "file_path": filepath,
            "user_email": getattr(current_user, "email", None)  # зберігаємо email
        })

        process_image.delay(
            job_id=job_id,
            filename=filename,
            filepath=filepath,
            user_email=getattr(current_user, "email", None)
        )

        return jsonify({
            "input": filename,
            "result": {
                "message": "Image conversion queued",
                "job_id": job_id,
                "status": "queued",
                "file": filepath
            }
        }), 200

    data = request.get_json(silent=True) or {}
    query = data.get("query")

    if not query:
        return jsonify({"error": "Missing 'query' field or file"}), 400

    try:
        if query.startswith("http://") or query.startswith("https://"):
            job_id = f"agent-parse-{uuid.uuid4().hex}"

            current_app.jobs.insert_one({
                "job_id": job_id,
                "status": "queued",
                "progress": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "url": query,
                "user_email": getattr(current_user, "email", None)
            })

            parse_page.delay(
                job_id=job_id,
                url=query,
                user_email=getattr(current_user, "email", None),
                limit=5
            )

            return jsonify({
                "input": query,
                "result": {
                    "message": "Parsing queued",
                    "job_id": job_id,
                    "status": "queued"
                }
            }), 200

        result = run_agent(query)
        return jsonify({
            "input": query,
            "result": result
        }), 200

    except Exception as e:
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
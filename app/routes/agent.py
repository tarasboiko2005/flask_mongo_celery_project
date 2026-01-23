from flask import Blueprint, request, jsonify, current_app
import os, uuid
from app.mcp.agent import run_agent
from app.tasks.parser_tasks import parse_page
from app.tasks.image_tasks import process_image
from app.repositories.job_repository import create_job

agent_bp = Blueprint("agent", __name__)

@agent_bp.route("/agent", methods=["POST"])
def post_agent():
    """
    Run agent with query (text or URL)
    ---
    tags:
      - Agent
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            query:
              type: string
              description: Text query or URL
    responses:
      200:
        description: Agent response
      400:
        description: Missing query field
      500:
        description: Internal error
    """
    data = request.get_json(force=True) or {}
    query = data.get("query")

    if not query:
        return jsonify({"error": "Missing 'query' field"}), 400

    try:
        # Якщо query виглядає як URL → запускаємо парсинг
        if query.startswith("http://") or query.startswith("https://"):
            job_id = f"agent-parse-{uuid.uuid4().hex}"
            create_job(job_id, "parse", {"url": query})
            parse_page.delay(job_id=job_id, url=query, limit=5)

            return jsonify({
                "input": query,
                "result": {
                    "message": "Parsing queued",
                    "job_id": job_id,
                    "status": "queued"
                }
            }), 200

        # Інакше → звичайний текстовий запит
        result = run_agent(query)
        return jsonify({
            "input": query,
            "result": result
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@agent_bp.route("/agent/image", methods=["POST"])
def post_agent_image():
    """
    Upload image for conversion (grayscale)
    ---
    tags:
      - Agent
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
    responses:
      202:
        description: Image conversion job queued
    """
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "file_required"}), 400

    filename = file.filename
    output_dir = os.getenv("FILE_OUTPUT_DIR", "./output")
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    file.save(filepath)

    job_id = f"agent-image-{uuid.uuid4().hex}"
    create_job(job_id, "agent_image", {"filename": filename, "filepath": filepath})

    process_image.delay(job_id=job_id, filename=filename, filepath=filepath)

    return jsonify({
        "input": filename,
        "result": {
            "message": "Image conversion queued",
            "job_id": job_id,
            "status": "queued",
            "file": filepath
        }
    }), 202
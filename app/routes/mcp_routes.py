from flask import Blueprint, request, jsonify
from app.mcp.tools import convert_tool, parse_tool
from app.rag.vector_store import get_vectorstore
from app.repositories.job_repository import create_job, get_job, update_job, delete_job

mcp_bp = Blueprint("mcp", __name__)

@mcp_bp.route("/convert_image", methods=["POST"])
def convert_image():
    """
    Convert image to grayscale
    ---
    tags:
      - MCP Tools
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            filename:
              type: string
            filepath:
              type: string
    responses:
      200:
        description: Conversion result
    """
    data = request.get_json(force=True)
    filename = data.get("filename")
    filepath = data.get("filepath")
    return jsonify({"output": convert_tool(filename, filepath)})

@mcp_bp.route("/parse_page", methods=["POST"])
def parse_page():
    """
    Parse images from a webpage
    ---
    tags:
      - MCP Tools
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            job_id:
              type: string
            url:
              type: string
            limit:
              type: integer
    responses:
      200:
        description: Task submission result
    """
    data = request.get_json(force=True)
    job_id = data.get("job_id")
    url = data.get("url")
    limit = data.get("limit", 5)
    return jsonify(parse_tool(job_id, url, limit))

@mcp_bp.route("/search_vectors", methods=["POST"])
def search_vectors():
    """
    Semantic search in FAISS vectorstore
    ---
    tags:
      - MCP Tools
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            query:
              type: string
            top_k:
              type: integer
    responses:
      200:
        description: Search results
    """
    data = request.get_json(force=True)
    query = data.get("query")
    top_k = data.get("top_k", 5)
    vs = get_vectorstore()
    results = vs.similarity_search(query, k=top_k)
    return jsonify({"output": [r.page_content for r in results]})

@mcp_bp.route("/create_job", methods=["POST"])
def create_job_tool():
    """
    Create a new job
    ---
    tags:
      - MCP Tools
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            job_id:
              type: string
            status:
              type: string
            progress:
              type: integer
    responses:
      200:
        description: Job created
    """
    data = request.get_json(force=True)
    job = create_job(data["job_id"], data.get("status", "pending"), data.get("progress", 0))
    return jsonify({"output": {"job_id": job.job_id, "status": job.status, "progress": job.progress}})

@mcp_bp.route("/get_job", methods=["POST"])
def get_job_tool():
    """
    Get job by ID
    ---
    tags:
      - MCP Tools
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            job_id:
              type: string
    responses:
      200:
        description: Job details
    """
    data = request.get_json(force=True)
    job = get_job(data["job_id"])
    if job:
        return jsonify({"output": {"job_id": job.job_id, "status": job.status, "progress": job.progress}})
    return jsonify({"output": None})

@mcp_bp.route("/update_job", methods=["POST"])
def update_job_tool():
    """
    Update job fields
    ---
    tags:
      - MCP Tools
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            job_id:
              type: string
            status:
              type: string
            progress:
              type: integer
    responses:
      200:
        description: Updated job
    """
    data = request.get_json(force=True)
    job = update_job(data["job_id"], **{k: v for k, v in data.items() if k != "job_id"})
    if job:
        return jsonify({"output": {"job_id": job.job_id, "status": job.status, "progress": job.progress}})
    return jsonify({"output": None})

@mcp_bp.route("/delete_job", methods=["POST"])
def delete_job_tool():
    """
    Delete job by ID
    ---
    tags:
      - MCP Tools
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            job_id:
              type: string
    responses:
      200:
        description: Deletion result
    """
    data = request.get_json(force=True)
    job = delete_job(data["job_id"])
    return jsonify({"output": bool(job)})
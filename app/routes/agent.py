from flask import Blueprint, request, jsonify
from app.mcp.agent import run_agent

agent_bp = Blueprint("agent", __name__)

@agent_bp.route("/agent", methods=["POST"])
def post_agent():
    """
    Run agent with query
    ---
    tags:
      - Agent
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            query:
              type: string
    responses:
      200:
        description: Agent response
    """
    data = request.get_json(force=True)
    query = data.get("query")
    result = run_agent(query)
    return jsonify({"output": result})
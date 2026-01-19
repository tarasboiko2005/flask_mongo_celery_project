from flask import Blueprint, request, jsonify
from flasgger import swag_from
from app.mcp.agent import run_agent

agent_bp = Blueprint("agent", __name__)

@agent_bp.route("/agent", methods=["POST"])
@swag_from({
    'tags': ['Agent'],
    'parameters': [
        {
            'name': 'query',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'query': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'LLM agent response',
            'schema': {
                'type': 'object',
                'properties': {
                    'answer': {'type': 'string'}
                }
            }
        }
    }
})
def agent_query():
    query = request.json.get("query")
    answer = run_agent(query)
    return jsonify({"answer": answer})
import json
import redis
from langchain.agents import initialize_agent
from langchain.tools import Tool
from app.mcp.tools import convert_tool, parse_tool
from app.rag.embeddings import get_llm
from app.rag.rag_pipeline import query_history
from app.settings import Settings

llm = get_llm()
r = redis.Redis(host=Settings.REDIS_HOST, port=Settings.REDIS_PORT, db=0)

def convert_image_wrapper(query: str):
    try:
        filename, filepath = query.split("|")
    except ValueError:
        return {
            "job_id": "CONVERT_ERROR",
            "status": "failed",
            "message": "Invalid format. Use 'filename|filepath'."
        }
    return convert_tool(filename, filepath)

def parse_page_wrapper(query: str):
    limit = 5
    result = parse_tool(url=query, limit=limit)
    return {
        "message": "Parsing end",
        "job_id": result.get("job_id"),
        "status": result.get("status", "unknown"),
        "file": result.get("file", "N/A"),
        "images_found": result.get("images", [])
    }

def rag_wrapper(query: str):
    answer = query_history(query)
    return {
        "job_id": "RAG_001",
        "status": "success",
        "answer": answer
    }

tools = [
    Tool(
        name="convert_image",
        func=convert_image_wrapper,
        description="Convert an image to grayscale. Input format: 'filename|filepath'",
        return_direct=True
    ),
    Tool(
        name="parse_page",
        func=parse_page_wrapper,
        description="Parse images from a webpage. Input: URL string",
        return_direct=True
    ),
    Tool(
        name="rag_query",
        func=rag_wrapper,
        description="Answer questions using the RAG knowledge base",
        return_direct=True
    )
]

agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    handle_parsing_errors=True,
    verbose=True,
    max_iterations=2
)

def run_agent(query: str):
    cached = r.get(query)
    if cached:
        return json.loads(cached)
    result = agent.invoke(query)
    r.set(query, json.dumps(result), ex=3600)
    return result
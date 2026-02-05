import ast
import json
from typing import Any

import redis
from langchain_classic.agents import initialize_agent
from langchain_classic.tools import Tool

from app.mcp.prompt import AGENT_MESSAGE, AGENT_SYSTEM_INSTRUCTIONS
from app.mcp.tools import convert_tool, parse_tool
from app.rag.embeddings import get_llm
from app.rag.rag_pipeline import query_history
from app.settings import Settings

llm = get_llm()
r = redis.from_url(Settings.REDIS_URL, decode_responses=True)


def convert_image_wrapper(query: str):
    try:
        parts = [p.strip() for p in query.split("|")]
        filename = parts[0]
        filepath = parts[1]
        user_email = parts[2] if len(parts) >= 3 and parts[2] else None
    except ValueError:
        return {
            "agent_message": AGENT_MESSAGE,
            "job_id": "CONVERT_ERROR",
            "status": "failed",
            "message": "Invalid format. Use 'filename|filepath' or 'filename|filepath|user_email'.",
        }
    result = convert_tool(filename, filepath, user_email=user_email)
    return {"agent_message": AGENT_MESSAGE, **result}


def parse_page_wrapper(query: str):
    limit = 5
    result = parse_tool(url=query, limit=limit)
    return {
        "agent_message": AGENT_MESSAGE,
        "message": "Parsing finished",
        "job_id": result.get("job_id"),
        "status": result.get("status", "unknown"),
        "file": result.get("file", "N/A"),
        "images_found": result.get("images", []),
    }


def rag_wrapper(query: str):
    answer = query_history(query)
    return {
        "agent_message": AGENT_MESSAGE,
        "job_id": "RAG_001",
        "status": "success",
        "answer": answer,
    }


tools = [
    Tool(
        name="convert_image",
        func=convert_image_wrapper,
        description=(
            "Convert an image to grayscale. Input format: 'filename|filepath' "
            "or 'filename|filepath|user_email' (optional)."
        ),
        return_direct=True,
    ),
    Tool(
        name="parse_page",
        func=parse_page_wrapper,
        description="Parse images from a webpage. Input: URL string",
        return_direct=True,
    ),
    Tool(
        name="rag_query",
        func=rag_wrapper,
        description="Answer questions using the RAG knowledge base",
        return_direct=True,
    ),
]

agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    handle_parsing_errors=True,
    verbose=True,
    max_iterations=2,
)


def _output_to_text(output: Any) -> str:
    if output is None:
        return ""
    if isinstance(output, str):
        s = output.strip()
        if s.startswith("[") and s.endswith("]"):
            try:
                parsed = json.loads(s)
            except Exception:
                parsed = None
            if parsed is None:
                try:
                    parsed = ast.literal_eval(s)
                except Exception:
                    parsed = None
            if parsed is not None and not isinstance(parsed, str):
                return _output_to_text(parsed)
        return output
    if isinstance(output, (list, tuple)):
        parts: list[str] = []
        for item in output:
            if item is None:
                continue
            if isinstance(item, str):
                if item.strip():
                    parts.append(item)
                continue
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str) and text.strip():
                    parts.append(text)
                    continue
                parts.append(json.dumps(item, ensure_ascii=False))
                continue
            parts.append(str(item))
        return "\n".join([p for p in parts if p.strip()])
    if isinstance(output, dict):
        if isinstance(output.get("answer"), str):
            return output["answer"]
        if isinstance(output.get("message"), str):
            return output["message"]
        return json.dumps(output, ensure_ascii=False)
    return str(output)


def _should_use_tools(query: str) -> bool:
    q = query.strip().lower()
    return any(
        key in q
        for key in (
            "rag",
            "knowledge base",
            "use tool",
            "parse_page",
            "convert_image",
        )
    )


def run_agent(query: str, *, debug: bool = False) -> dict:
    cache_key = f"agent:v2:{int(debug)}:{query}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    prompt = f"{AGENT_SYSTEM_INSTRUCTIONS}\nUser: {query}"

    if not _should_use_tools(query):
        msg = llm.invoke(prompt)
        content = getattr(msg, "content", msg)
        answer_text = _output_to_text(content).strip()
        response: dict = {"agent_message": AGENT_MESSAGE, "answer": answer_text}
        r.set(cache_key, json.dumps(response, ensure_ascii=False), ex=3600)
        return response

    raw_result = agent.invoke(prompt)
    raw_output = (
        raw_result.get("output") if isinstance(raw_result, dict) else raw_result
    )
    answer_text = _output_to_text(raw_output).strip()

    response = {"agent_message": AGENT_MESSAGE, "answer": answer_text}
    if debug:
        response["result"] = raw_result

    r.set(cache_key, json.dumps(response, ensure_ascii=False), ex=3600)
    return response

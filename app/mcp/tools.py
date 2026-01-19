import os
from celery import Celery
from app.tasks.image_tasks import register_image_tasks
from app.tasks.parser_tasks import register_parser_tasks

celery = Celery(
    "mcp_tools",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
)

process_image_task = register_image_tasks(celery)
parse_page_task = register_parser_tasks(celery)

def convert_tool(filename: str = None, filepath: str = None):
    if not filename or not filepath:
        return "You must provide filename and filepath"
    return f"Converted {filename} at {filepath} to grayscale"

def parse_tool(job_id: str, url: str, limit: int = 5):
    async_result = parse_page_task.delay(job_id, url, limit)
    return {"task_id": async_result.id, "status": "submitted"}
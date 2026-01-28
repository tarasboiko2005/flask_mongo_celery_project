import logging
import uuid
import os
from datetime import datetime
from pymongo import MongoClient
from app.tasks.image_tasks import process_image
from app.tasks.parser_tasks import parse_page

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_job_record(job_id: str, job_type: str, extra: dict = None):
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client.get_default_database()
        jobs = db["jobs"]

        base_record = {
            "job_id": job_id,
            "type": job_type,
            "status": "queued",
            "progress": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "parsed_data": [],
            "processed_files": []
        }
        if extra:
            base_record.update(extra)

        jobs.insert_one(base_record)
        logger.info(f"[{job_id}] Job record created in MongoDB")
    except Exception as e:
        logger.error(f"[{job_id}] Failed to create job record: {e}")

def convert_tool(filename: str, filepath: str) -> dict:
    try:
        job_id = f"convert-{uuid.uuid4().hex}"
        create_job_record(job_id, "convert", {"filename": filename, "filepath": filepath})
        process_image.delay(job_id=job_id, filename=filename, filepath=filepath)

        return {
            "job_id": job_id,
            "filename": filename,
            "filepath": filepath,
            "status": "queued",
            "message": f"Conversion task for {filename} has been queued.",
            "output_file": None
        }

    except Exception as e:
        logger.error(f"[convert_tool] Failed to queue conversion: {e}")
        return {
            "job_id": None,
            "filename": filename,
            "filepath": filepath,
            "status": "failed",
            "message": f"Failed to queue conversion task: {str(e)}",
            "output_file": None
        }

def parse_tool(url: str, limit: int = 5) -> dict:
    try:
        job_id = f"parse-{uuid.uuid4().hex}"
        create_job_record(job_id, "parse", {"url": url})
        parse_page.delay(job_id=job_id, url=url, limit=limit)

        return {
            "job_id": job_id,
            "status": "queued",
            "message": f"Parsing task for {url} has been queued.",
            "images": [],
            "file": None
        }

    except Exception as e:
        logger.error(f"[parse_tool] Failed to queue parsing: {e}")
        return {
            "job_id": None,
            "status": "failed",
            "message": f"Failed to queue parsing task: {str(e)}",
            "images": [],
            "file": None
        }
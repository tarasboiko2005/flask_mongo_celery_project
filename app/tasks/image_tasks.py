import os
import logging
from datetime import datetime
from pymongo import MongoClient
from PIL import Image
from celery import shared_task
from app.schemas import JobStatusResponse
from app.tasks.email_tasks import send_job_report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@shared_task(name="tasks.process_image", bind=True)
def process_image(self, job_id: str, filename: str, filepath: str, user_email: str):
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client.get_default_database()
    jobs = db["jobs"]

    jobs.update_one(
        {"job_id": job_id},
        {"$set": {
            "status": "processing",
            "progress": 25,
            "updated_at": datetime.utcnow()
        }}
    )

    logger.info(f"[{job_id}] Start processing {filename}")

    try:
        img = Image.open(filepath).convert("L")
        output_dir = os.getenv("FILE_OUTPUT_DIR", "./output")
        os.makedirs(output_dir, exist_ok=True)
        name, ext = os.path.splitext(filename)
        new_filename = f"processed_{name}{ext}"
        new_filepath = os.path.join(output_dir, new_filename)
        img.save(new_filepath)
        result = JobStatusResponse(
            job_id=job_id,
            status="ready",
            progress=100,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            filename=new_filename,
            file_path=new_filepath
        )

        jobs.update_one(
            {"job_id": job_id},
            {"$set": result.model_dump(mode="json")}
        )

        logger.info(f"[{job_id}] Finished processing")
        send_job_report.delay(
            user_email,
            job_id,
            "ready",
            f"Image {filename} processed successfully and saved as {new_filename}"
        )
        return result.model_dump(mode="json")

    except Exception as e:
        logger.exception(f"[{job_id}] Failed to process image")

        jobs.update_one(
            {"job_id": job_id},
            {"$set": {
                "status": "failed",
                "progress": 100,
                "updated_at": datetime.utcnow()
            }}
        )
        send_job_report.delay(
            user_email,
            job_id,
            "failed",
            f"Error while processing {filename}: {str(e)}"
        )

        return {"error": str(e)}
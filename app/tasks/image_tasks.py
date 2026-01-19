from PIL import Image
import os
from datetime import datetime
from pymongo import MongoClient
import logging
from app.schemas import JobStatusResponse
from app.repositories.job_repository import update_job

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_image_tasks(celery):
    @celery.task(name="tasks.process_image")
    def process_image(job_id: str, filename: str, filepath: str):
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client.get_default_database()
        jobs = db["jobs"]

        jobs.update_one(
            {"job_id": job_id},
            {"$set": {"status": "processing", "progress": 25, "updated_at": datetime.utcnow()}}
        )
        update_job(job_id, status="processing", progress=25, updated_at=datetime.utcnow())
        logger.info(f"[{job_id}] Start processing {filename}")

        try:
            img = Image.open(filepath)
            img = img.convert("L")

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

            jobs.update_one({"job_id": job_id}, {"$set": result.model_dump(mode="json")})
            update_job(job_id, status="ready", progress=100, updated_at=datetime.utcnow(),
                       filename=new_filename, file_path=new_filepath)

            logger.info(f"[{job_id}] Finished processing")
            return result.model_dump(mode="json")

        except Exception as e:
            logger.error(f"[{job_id}] Failed to process image: {e}")
            jobs.update_one(
                {"job_id": job_id},
                {"$set": {"status": "failed", "progress": 100, "updated_at": datetime.utcnow()}}
            )
            update_job(job_id, status="failed", progress=100, updated_at=datetime.utcnow())
            return {"error": str(e)}

    return process_image
import os
import time
from datetime import datetime
from pymongo import MongoClient

def ensure_txt_extension(name: str) -> str:
    return name if os.path.splitext(name)[1] else f"{name}.txt"

def register_task(celery):
    @celery.task(name="tasks.generate_file")
    def generate_file(job_id: str, filename: str = None):
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client.get_default_database()
        jobs = db["jobs"]

        filename = ensure_txt_extension(filename or f"{job_id}.txt")
        filepath = os.path.join(os.getenv("FILE_OUTPUT_DIR", "./output"), filename)

        jobs.update_one({"job_id": job_id}, {"$set": {"status": "processing", "progress": 25, "updated_at": datetime.utcnow()}})
        time.sleep(2)
        jobs.update_one({"job_id": job_id}, {"$set": {"progress": 50, "updated_at": datetime.utcnow()}})
        time.sleep(2)
        jobs.update_one({"job_id": job_id}, {"$set": {"progress": 75, "updated_at": datetime.utcnow()}})
        time.sleep(2)

        time.sleep(5)

        with open(filepath, "w") as f:
            f.write(f"File for job {job_id} created at {datetime.utcnow()}")

        jobs.update_one(
            {"job_id": job_id},
            {"$set": {
                "status": "ready",
                "progress": 100,
                "updated_at": datetime.utcnow(),
                "file_path": filepath,
                "filename": filename
            }}
        )
        return filepath

    return generate_file
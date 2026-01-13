from PIL import Image
import os
from datetime import datetime
from pymongo import MongoClient

def register_image_tasks(celery):
    @celery.task(name="tasks.process_image")
    def process_image(job_id: str, filename: str, filepath: str):
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client.get_default_database()
        jobs = db["jobs"]

        jobs.update_one({"job_id": job_id}, {"$set": {"status": "processing", "progress": 25, "updated_at": datetime.utcnow()}})

        img = Image.open(filepath)
        img = img.convert("L")  # grayscale

        output_dir = os.getenv("FILE_OUTPUT_DIR", "./output")
        name, ext = os.path.splitext(filename)
        new_filename = f"processed_{name}{ext}"
        new_filepath = os.path.join(output_dir, new_filename)
        img.save(new_filepath)

        jobs.update_one(
            {"job_id": job_id},
            {"$set": {
                "status": "ready",
                "progress": 100,
                "updated_at": datetime.utcnow(),
                "file_path": new_filepath,
                "filename": new_filename
            }}
        )
        return new_filepath

    return process_image
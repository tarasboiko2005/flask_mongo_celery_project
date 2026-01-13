from bs4 import BeautifulSoup
import requests, os, uuid, logging
from datetime import datetime
from pymongo import MongoClient
from PIL import Image
from io import BytesIO
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_parser_tasks(celery):
    @celery.task(name="tasks.parse_page")
    def parse_page(job_id: str, url: str, limit: int = 5):

        client = MongoClient(os.getenv("MONGO_URI"))
        db = client.get_default_database()
        jobs = db["jobs"]

        jobs.update_one(
            {"job_id": job_id},
            {"$set": {"status": "processing", "progress": 25, "updated_at": datetime.utcnow()}}
        )

        logger.info(f"[{job_id}] Start parsing {url}")

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        images = [img["src"] for img in soup.find_all("img") if "src" in img.attrs]
        images = images[:limit]

        processed_files = []
        output_dir = os.getenv("FILE_OUTPUT_DIR", "./output")

        for src in images:
            try:
                full_url = urljoin(url, src)

                if not full_url.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                    logger.warning(f"[{job_id}] Skip unsupported format: {full_url}")
                    continue

                logger.info(f"[{job_id}] Downloading {full_url}")
                img_resp = requests.get(full_url, timeout=5)
                img_resp.raise_for_status()

                img = Image.open(BytesIO(img_resp.content)).convert("L")

                filename = f"parsed_{uuid.uuid4().hex}.png"
                filepath = os.path.join(output_dir, filename)
                img.save(filepath)

                processed_files.append({"filename": filename, "file_path": filepath})
                logger.info(f"[{job_id}] Saved {filename}")

            except Exception as e:
                logger.error(f"[{job_id}] Failed to process {src}: {e}")
                continue

        jobs.update_one(
            {"job_id": job_id},
            {"$set": {
                "status": "ready",
                "progress": 100,
                "updated_at": datetime.utcnow(),
                "parsed_data": images,
                "processed_files": processed_files
            }}
        )
        logger.info(f"[{job_id}] Finished parsing. Files: {len(processed_files)}")
        return processed_files

    return parse_page
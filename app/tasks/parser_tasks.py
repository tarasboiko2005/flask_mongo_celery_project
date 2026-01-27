import os, uuid, logging, requests
from datetime import datetime
from pymongo import MongoClient
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from urllib.parse import urljoin
from app.schemas import ParsedImage, ParseResult
from app.repositories.job_repository import update_job
from app.rag.vector_store import add_metadata

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
        update_job(job_id, status="processing", progress=25, updated_at=datetime.utcnow())
        logger.info(f"[{job_id}] Start parsing {url}")

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"[{job_id}] Failed to fetch page: {e}")
            jobs.update_one({"job_id": job_id}, {"$set": {"status": "failed", "progress": 100}})
            update_job(job_id, status="failed", progress=100, updated_at=datetime.utcnow())
            return {"error": str(e)}

        soup = BeautifulSoup(response.text, "html.parser")
        images = []
        for img in soup.find_all("img"):
            if "src" in img.attrs:
                full_url = urljoin(url, img["src"])
                images.append(full_url)

        images = images[:limit]
        logger.info(f"[{job_id}] Found {len(images)} images")

        processed_files = []
        output_dir = os.getenv("FILE_OUTPUT_DIR", "./output")
        os.makedirs(output_dir, exist_ok=True)

        for full_url in images:
            try:
                if not full_url.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
                    logger.warning(f"[{job_id}] Skip unsupported format: {full_url}")
                    continue

                logger.info(f"[{job_id}] Downloading {full_url}")
                img_resp = requests.get(full_url, timeout=5)
                img_resp.raise_for_status()

                img = Image.open(BytesIO(img_resp.content)).convert("L")

                filename = f"parsed_{uuid.uuid4().hex}.png"
                filepath = os.path.join(output_dir, filename)
                img.save(filepath)

                processed_file = ParsedImage(
                    filename=filename,
                    file_path=filepath,
                    source_url=full_url
                )
                processed_files.append(processed_file)

                metadata = f"Parsed image {filename} from {full_url} at {datetime.utcnow()}"
                add_metadata(metadata)

                logger.info(f"[{job_id}] Saved {filename}")

            except Exception as e:
                logger.error(f"[{job_id}] Failed to process {full_url}: {e}")
                continue

        status = "ready" if processed_files else "failed"

        try:
            result = ParseResult(
                job_id=job_id,
                status=status,
                progress=100,
                updated_at=datetime.utcnow(),
                parsed_data=images,
                processed_files=processed_files
            )
        except Exception as e:
            logger.error(f"[{job_id}] Validation failed: {e}")
            jobs.update_one({"job_id": job_id}, {"$set": {"status": "failed", "progress": 100}})
            update_job(job_id, status="failed", progress=100, updated_at=datetime.utcnow())
            return {"error": str(e)}

        jobs.update_one({"job_id": job_id}, {"$set": result.model_dump(mode="json")})
        update_job(job_id, status=status, progress=100, updated_at=datetime.utcnow())

        logger.info(f"[{job_id}] Finished parsing. Files: {len(processed_files)}")
        return result.model_dump(mode="json")

    return parse_page
from celery import shared_task
import os, uuid, logging, requests
from datetime import datetime
from pymongo import MongoClient
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from urllib.parse import urljoin
from app.schemas import ParsedImage, ParseResult
from app.rag.vector_store import add_metadata
from app.tasks.email_tasks import send_job_report

logger = logging.getLogger(__name__)

@shared_task(name="tasks.parse_page")
def parse_page(job_id: str, url: str, user_email: str, limit: int = 5):
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client.get_default_database()
    jobs = db["jobs"]

    jobs.update_one({"job_id": job_id}, {
        "$set": {"status": "processing", "progress": 25, "updated_at": datetime.utcnow()}
    })

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        jobs.update_one({"job_id": job_id}, {"$set": {"status": "failed", "progress": 100}})
        send_job_report.delay(user_email, job_id, "failed", f"Error fetching {url}: {str(e)}")
        return {"error": str(e)}
    soup = BeautifulSoup(response.text, "html.parser")
    images = [urljoin(url, img["src"]) for img in soup.find_all("img") if "src" in img.attrs][:limit]
    processed_files = []
    output_dir = os.getenv("FILE_OUTPUT_DIR", "./output")
    os.makedirs(output_dir, exist_ok=True)

    for full_url in images:
        try:
            if not full_url.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
                continue
            img_resp = requests.get(full_url, timeout=5)
            img_resp.raise_for_status()
            img = Image.open(BytesIO(img_resp.content)).convert("L")

            filename = f"parsed_{uuid.uuid4().hex}.png"
            filepath = os.path.join(output_dir, filename)
            img.save(filepath)

            processed_files.append(ParsedImage(filename=filename, file_path=filepath, source_url=full_url))
            add_metadata(f"Parsed image {filename} from {full_url} at {datetime.utcnow()}")

        except Exception as e:
            logger.error(f"[{job_id}] Failed to process {full_url}: {e}")
            continue

    status = "ready" if processed_files else "failed"
    result = ParseResult(
        job_id=job_id,
        status=status,
        progress=100,
        updated_at=datetime.utcnow(),
        parsed_data=images,
        processed_files=processed_files
    )

    jobs.update_one({"job_id": job_id}, {"$set": result.model_dump(mode="json")})
    if status == "ready":
        send_job_report.delay(user_email, job_id, "ready", f"Parsed {len(processed_files)} images from {url}")
    else:
        send_job_report.delay(user_email, job_id, "failed", f"No images could be processed from {url}")
    return result.model_dump(mode="json")
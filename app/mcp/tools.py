def convert_tool(filename: str, filepath: str) -> str:
    return f"Converted {filename} at {filepath} to grayscale"

def parse_tool(job_id: str, url: str, limit: int = 5) -> dict:
    return {"job_id": job_id, "url": url, "images_found": limit}
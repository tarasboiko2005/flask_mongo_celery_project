from pydantic import BaseModel, HttpUrl, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class ImageUploadRequest(BaseModel):
    filename: str = Field(min_length=1)

class ParseJobRequest(BaseModel):
    url: HttpUrl
    limit: Optional[int] = Field(default=5, ge=1, le=100)

class ProcessedFile(BaseModel):
    filename: str
    file_path: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    created_at: datetime
    updated_at: datetime
    filename: Optional[str] = None
    file_path: Optional[str] = None
    processed_files: Optional[List[ProcessedFile]] = None
    url: Optional[HttpUrl] = None
    limit: Optional[int] = None
    parsed_data: Optional[List[HttpUrl]] = None

class ParsedImage(BaseModel):
    filename: str
    file_path: str
    source_url: HttpUrl

class ParseResult(BaseModel):
    job_id: str
    status: str
    progress: int
    parsed_data: List[HttpUrl]
    processed_files: List[ParsedImage]
    updated_at: datetime

class SendJobReportRequest(BaseModel):
    user_email: EmailStr
    job_id: str
    status: str
    details: str

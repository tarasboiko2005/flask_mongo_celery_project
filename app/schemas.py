from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class ImageUploadRequest(BaseModel):
    filename: str = Field(min_length=1)


class ParseJobRequest(BaseModel):
    url: HttpUrl
    limit: int | None = Field(default=5, ge=1, le=100)


class ProcessedFile(BaseModel):
    filename: str
    file_path: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    created_at: datetime
    updated_at: datetime
    filename: str | None = None
    file_path: str | None = None
    processed_files: list[ProcessedFile] | None = None
    url: HttpUrl | None = None
    limit: int | None = None
    parsed_data: list[HttpUrl] | None = None


class ParsedImage(BaseModel):
    filename: str
    file_path: str
    source_url: HttpUrl


class ParseResult(BaseModel):
    job_id: str
    status: str
    progress: int
    parsed_data: list[HttpUrl]
    processed_files: list[ParsedImage]
    updated_at: datetime


class SendJobReportRequest(BaseModel):
    user_email: EmailStr
    job_id: str
    status: str
    details: str

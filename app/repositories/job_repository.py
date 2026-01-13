from app.db import db
from app.models import Job

def create_job(job_id: str, status: str = "pending", progress: int = 0):
    job = Job(job_id=job_id, status=status, progress=progress)
    db.session.add(job)
    db.session.commit()
    return job

def get_job(job_id: str):
    return Job.query.filter_by(job_id=job_id).first()

def update_job(job_id: str, **kwargs):
    job = Job.query.filter_by(job_id=job_id).first()
    if job:
        for key, value in kwargs.items():
            setattr(job, key, value)
        db.session.commit()
    return job

def delete_job(job_id: str):
    job = Job.query.filter_by(job_id=job_id).first()
    if job:
        db.session.delete(job)
        db.session.commit()
    return job
from datetime import datetime
from app.extensions import db
from app.models import Job
from app.tasks.email_tasks import send_job_report
from flask_login import current_user

def create_job(job_id: str, status: str = "pending", progress: int = 0):
    job = Job(job_id=job_id, status=status, progress=progress, updated_at=datetime.utcnow())
    db.session.add(job)
    db.session.commit()
    return job

def get_job(job_id: str):
    return Job.query.filter_by(job_id=job_id).first()

def update_job(job_id, **kwargs):
    job = Job.query.filter_by(job_id=job_id).first()
    if job:
        for key, value in kwargs.items():
            setattr(job, key, value)
        job.updated_at = datetime.utcnow()
        db.session.commit()

        if "status" in kwargs and current_user.is_authenticated:
            send_job_report.delay(
                current_user.email,
                job.job_id,
                job.status,
                kwargs.get("details", "Job updated")
            )

    return job

def delete_job(job_id: str):
    job = Job.query.filter_by(job_id=job_id).first()
    if job:
        db.session.delete(job)
        db.session.commit()
    return job
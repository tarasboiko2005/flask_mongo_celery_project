# app/tasks/email_tasks.py
import os
from app.extensions import celery

# Імпортуємо тільки моделі та функції, потрібні для email
from app.models import Job, User
from app.utils.email import send_email

@celery.task
def send_job_report(job_id, user_id):
    print("MAIL_PASSWORD in Celery:", os.getenv("MAIL_PASSWORD"))

    job = Job.query.get(job_id)
    user = User.query.get(user_id)

    if not job:
        print(f"[ERROR] Job {job_id} not found.")
        return
    if not user:
        print(f"[ERROR] User {user_id} not found.")
        return

    subject = f"Report #{job.job_id}"
    body = f"""
    Hello {user.name},

    Your job has finished.
    ID: {job.job_id}
    Status: {job.status}
    Details: {getattr(job, 'details', 'No details provided')}

    Thank you for using our service!
    """
    try:
        send_email(subject, [user.email], body)
        print(f"[INFO] Report email sent to {user.email}")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")

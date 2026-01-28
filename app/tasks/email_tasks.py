from app.utils.email import send_email
from app.extensions import celery
import os

print("MAIL_PASSWORD in Celery:", os.getenv("MAIL_PASSWORD"))
@celery.task
def send_job_report(user_email, job_id, status, details):
    subject = f"Report #{job_id}"
    body = f"""
    Hello,

    Your job has finished.
    ID: {job_id}
    Status: {status}
    Details: {details}

    Thank you for using our service!
    """
    send_email(subject, [user_email], body)
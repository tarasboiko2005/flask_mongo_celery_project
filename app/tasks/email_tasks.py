from app.extensions import celery, mail
from app import create_app
from flask_mail import Message

app = create_app()


@celery.task
def send_job_report(user_email, job_id, status=None, details=None):
    if not user_email:
        raise ValueError("No recipient email provided")

    subject = f"Report #{job_id}"
    body = f"""
Hello,

Your job has finished.
ID: {job_id}
Status: {status or "N/A"}
Details: {details or "N/A"}

Thank you for using our service!
"""

    with app.app_context():
        msg = Message(subject=subject, recipients=[user_email], body=body)
        try:
            mail.send(msg)
            print(f"📧 Email sent to {user_email}")
        except Exception as e:
            print(f"❌ Failed to send email to {user_email}: {e}")
            raise

# email_tasks_test.py
import os

def send_job_report_test(job, user):
    print("MAIL_PASSWORD:", os.getenv("MAIL_PASSWORD"))

    subject = f"Report #{job.job_id}"
    body = f"""
    Hello {user.name},

    Your job has finished.
    ID: {job.job_id}
    Status: {job.status}
    Details: {getattr(job, 'details', 'No details provided')}

    Thank you for using our service!
    """

    print("[INFO] Email would be sent here")
    print(subject)
    print(body)

# Fake data
class FakeUser:
    id = 1
    name = "Test User"
    email = "test@example.com"

class FakeJob:
    id = 1
    job_id = 123
    status = "finished"
    details = "All good"

send_job_report_test(FakeJob(), FakeUser())

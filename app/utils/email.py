from flask_mail import Message
from app.extensions import mail
from flask import current_app

def send_email(subject, recipients, body):
    recipients = [r for r in recipients if r]
    if not recipients:
        raise ValueError("No valid recipient emails provided")

    print("=== Sending email ===")
    print("Recipients:", recipients)
    print("Subject:", subject)
    print("Body:", body)

    msg = Message(
        subject=subject,
        sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
        recipients=recipients,
        body=body
    )
    try:
        mail.send(msg)
        print("=== Email sent successfully ===")
    except Exception as e:
        print("=== Failed to send email ===")
        print("Error:", e)
        raise
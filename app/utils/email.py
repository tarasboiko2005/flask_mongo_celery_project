from flask_mail import Message
from app.extensions import mail
from flask import current_app

def send_email(subject, recipients, body):
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
    mail.send(msg)

    print("=== Email queued successfully ===")
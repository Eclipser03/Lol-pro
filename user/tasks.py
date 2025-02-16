from django.conf import settings
from django.core.mail import EmailMessage

from lol_pay.celery import app


@app.task
def send_email_task(subject, message, recipient_list, from_email=None):
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        to=recipient_list,
    )
    email.content_subtype = 'html'
    email.send(fail_silently=False)

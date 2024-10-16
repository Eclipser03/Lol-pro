from django.conf import settings
from django.core.mail import send_mail

from lol_pay.celery import app


@app.task
def send_email_task(subject, message, recipient_list, from_email=None):
    send_mail(
        subject,
        message,
        from_email or settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )

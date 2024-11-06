from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage

from lol_pay.celery import app


@app.task
def send_email_task(subject, message, recipient_list, from_email=None):
    email = EmailMessage(
        subject=subject,
        body=message,  # Это будет HTML-сообщение
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        to=recipient_list
    )
    # Указываем, что тело письма будет в формате HTML
    email.content_subtype = 'html'
    email.send(fail_silently=False)
    # send_mail(
    #     subject,
    #     message,
    #     from_email or settings.DEFAULT_FROM_EMAIL,
    #     recipient_list,
    #     fail_silently=False,
    #     html_message=message,
    # )

import logging
from copy import copy

from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.forms import BaseForm, model_to_dict
from django.http import HttpRequest, QueryDict
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from user.models import User
from user.tasks import send_email_task


logger = logging.getLogger('main')


def handle_form_errors(request: HttpRequest, form: BaseForm) -> None:
    """
    Обрабатывает ошибки формы: логирует их и добавляет в сообщения.
    """
    errors = form.errors.values()
    for error in errors:
        for text in error:
            logger.warning(f'Ошибка при обработке формы {form.__class__.__name__}: {text}')
            messages.error(request, text)


def form_fill(data: QueryDict, obj: User) -> dict:
    """Заполняет дату данными пользователя"""

    data = copy(data)
    for k, v in model_to_dict(obj).items():
        if k not in data:
            data[k] = v
    return data


def send_confirmation_email(user: User, request: HttpRequest, new_email: str) -> None:
    """
    Отправляет письмо для подтверждения изменения электронной почты.
    """

    new_email_encoded = urlsafe_base64_encode(force_bytes(new_email))
    current_site = get_current_site(request)
    mail_subject = 'Подтверждение изменения электронной почты'
    message = render_to_string(
        'user/confirm_email_change.html',
        {
            'user': user,
            'new_email': new_email_encoded,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': token_generator.make_token(user),
        },
    )

    send_email_task.delay(mail_subject, message, [user.email])


def authenticated_logger(request):
    logger.warning('Попытка оформления заказа без входа в аккаунт.')
    messages.warning(request, 'Пожалуйста, войдите в аккаунт, чтобы оформить заказ')

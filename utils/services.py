import logging

from django.contrib import messages
from django.forms import BaseForm
from django.http import HttpRequest


logger = logging.getLogger(__name__)


def handle_form_errors(request: HttpRequest, form: BaseForm) -> None:
    """
    Обрабатывает ошибки формы: логирует их и добавляет в сообщения.
    """
    errors = form.errors.values()
    for error in errors:
        for text in error:
            logger.warning(f'Ошибка при обработке формы {form.__class__.__name__}: {text}')
            messages.error(request, text)

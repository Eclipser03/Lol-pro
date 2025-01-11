import logging
from os import getenv
from statistics import mean

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.handlers.asgi import ASGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView
from proxy.views import proxy_view

from main.forms import ReviewsForm
from main.models import ReviewModel
from utils.mixins import TitleMixin
from utils.services import handle_form_errors


logger = logging.getLogger('main')


class HomeView(TitleMixin, TemplateView):
    template_name = 'main/index.html'
    title = 'Главная'


class ReviewsView(TitleMixin, ListView):
    template_name = 'main/reviews.html'
    title = 'Отзывы'
    paginate_by = 10
    model = ReviewModel
    context_object_name = 'reviews'

    def get_queryset(self):
        return ReviewModel.objects.filter(parent__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reviews = context['reviews']

        context['user_list'] = reviews.values_list('user', flat=True)
        context['average_stars'] = mean(reviews.values_list('stars', flat=True) or [0])
        context['form'] = ReviewsForm()

        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            logger.info('Анонимный пользователь попытался оставить отзыв')
            messages.warning(request, 'Пожалуйста, войдите в аккаунт, чтобы оставить отзыв')
            return redirect('user:login')

        form = ReviewsForm(request.POST)
        form.request = self.request

        if form.is_valid():
            form.save()
            logger.info(f'Пользователь {request.user.username} оставил отзыв')
        else:
            handle_form_errors(request, form)
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            context['form'] = form
            return render(request, self.template_name, context)

        return redirect('main:reviews')


def custom_404_view(request, exception):
    return render(request, 'errors/404.html', status=404)


def custom_500_view(request):
    return render(request, 'errors/500.html', status=500)


def custom_403_view(request, exception):
    return render(request, 'errors/403.html', status=403)


def custom_400_view(request, exception):
    return render(request, 'errors/400.html', status=400)


@csrf_exempt
def flower_proxy_view(request: ASGIRequest, path: str) -> HttpResponse:
    """Представление позволяющее открывать панель flower
    как обычную страницу django (только для супер пользователя)."""

    if not request.user.is_superuser:
        raise PermissionDenied
    return proxy_view(
        request,
        f"http://{getenv('CELERY_FLOWER_ADDRESS')}:{getenv('CELERY_FLOWER_PORT')}/{getenv('CELERY_FLOWER_URL_PREFIX')}/{path}",
        {},
    )

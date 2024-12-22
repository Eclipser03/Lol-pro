import logging
from math import e
from statistics import mean

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import ListView, TemplateView

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
        return ReviewModel.objects.filter(parent__isnull=True).order_by('-created_at')

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

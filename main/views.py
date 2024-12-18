import logging
from typing import Any

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from main.forms import ReviewsForm
from main.models import ReviewModel


logger = logging.getLogger('main')
# Create your views here.


class TitleMixin:
    title = 'default_title'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class HomeView(TitleMixin, TemplateView):
    template_name = 'main/index.html'
    title = 'Главная'



class ReviewsView(TitleMixin, TemplateView):
    template_name = 'main/reviews.html'
    title = 'Отзывы'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # context['reviews'] = ReviewModel.objects.filter(parent__isnull=True)

        reviews = ReviewModel.objects.filter(parent__isnull=True).order_by('-created_at')
        user_list = reviews.values_list('user', flat=True)
        user = self.request.user
        stars_list = list(map(int, reviews.values_list('stars', flat=True)))
        average_stars = sum(stars_list) / len(stars_list) if len(stars_list) >= 1 else 0

        print('USER LIST', stars_list)

        page_number = self.request.GET.get('page', 1)
        paginator = Paginator(reviews, 5)
        current_page = paginator.page(page_number)

        context['reviews'] = current_page
        context['paginator'] = paginator
        context['current_page'] = current_page
        context['form'] = ReviewsForm()
        context['user_list'] = user_list
        context['user'] = user
        context['average_stars'] = average_stars
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            logger.info('Анонимный пользователь попытался оставить отзыв')
            messages.warning(request, 'Пожалуйста, войдите в аккаунт, чтобы оставить отзыв')
            return redirect('user:login')
        form = ReviewsForm(request.POST)
        form.request = self.request
        print('POST', request.POST)
        if form.is_valid():
            form.save()
            logger.info(f'Пользователь {request.user.username} оставил отзыв')
        else:
            errors = form.errors.values()
            print(form.errors)
            for error in errors:
                for text in error:
                    logger.warning(f'Ошибка при оставлении отзыва: {text}')
                    messages.error(request, text)
            return render(request, self.template_name, {'form': form})
        return redirect('main:reviews')

def custom_404_view(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500_view(request):
    return render(request, 'errors/500.html', status=500)

def custom_403_view(request, exception):
    return render(request, 'errors/403.html', status=403)

def custom_400_view(request, exception):
    return render(request, 'errors/400.html', status=400)

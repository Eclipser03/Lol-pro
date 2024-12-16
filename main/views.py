from typing import Any

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from main.forms import ReviewsForm
from main.models import ReviewModel


# Create your views here.

class TitleMixin:
    title = 'default_title'
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
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
            messages.warning(request, 'Пожалуйста, войдите в аккаунт, чтобы оформить заказ')
            return redirect('user:login')
        form = ReviewsForm(request.POST)
        form.request = self.request
        print('POST', request.POST)
        if form.is_valid():
            form.save()
        else:
            errors = form.errors.values()
            print(form.errors)
            for error in errors:
                for text in error:
                    messages.error(request, text)
            return render(request, self.template_name, {'form': form})
        return redirect('main:reviews')

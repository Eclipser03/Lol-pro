from typing import Any

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from main.forms import ReviewsForm
from main.models import ReviewModel


# Create your views here.


class HomeView(TemplateView):
    template_name = 'main/index.html'


class ReviewsView(TemplateView):
    template_name = 'main/reviews.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # context['reviews'] = ReviewModel.objects.filter(parent__isnull=True)

        reviews = ReviewModel.objects.filter(parent__isnull=True).order_by('-created_at')

        page_number = self.request.GET.get('page', 1)
        paginator = Paginator(reviews, 5)
        current_page = paginator.page(page_number)

        context['reviews'] = current_page
        context['paginator'] = paginator
        context['current_page'] = current_page
        context['form'] = ReviewsForm()
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

from typing import Any
from django.views.generic import TemplateView

from main.models import ReviewModel


# Create your views here.


class HomeView(TemplateView):
    template_name = 'main/index.html'

class ReviewsView(TemplateView):
    template_name = 'main/reviews.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['reviews'] = ReviewModel.objects.all()
        return context

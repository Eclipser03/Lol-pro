from django.views.generic import ListView

from main.views import TitleMixin
from news.models import News


class NewsView(TitleMixin, ListView):
    template_name = 'news/news.html'
    paginate_by = 12
    model = News
    context_object_name = 'news_items'
    title = 'Новости лиги'

from django.views.generic import ListView

from news.models import News
from news.services import parse_news
from main.views import TitleMixin


# Create your views here.

# Отображение списка новостей


class NewsView(TitleMixin, ListView):
    template_name = 'news/news.html'
    paginate_by = 12
    model = News
    context_object_name = 'news_items'
    ordering = ('-date_published',)
    title = 'Новости'
    # parse_news()

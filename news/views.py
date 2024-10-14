from django.views.generic import ListView

from news.models import News


# Create your views here.

# Отображение списка новостей

class NewsView(ListView):
    template_name = 'news/news.html'
    paginate_by = 12
    model = News
    context_object_name = 'news_items'
    ordering = ('-date_published',)

    # def get_context_data(self, **kwargs):
    # context = super().get_context_data(**kwargs)  # Получаем стандартный контекст
    #     news_items = News.objects.all()
    #     print(news_items)

    #     paginator = Paginator(news_items, 12)
    #     page_number = self.request.GET.get('page')
    #     news_page = paginator.get_page(page_number)

    #     context['news_items'] = news_page  # Добавляем список новостей в контекст
    #     return context

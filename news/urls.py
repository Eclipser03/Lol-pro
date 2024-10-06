from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from news.views import NewsView

app_name = 'news'

urlpatterns = [
    path('news/', NewsView.as_view(), name='news'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

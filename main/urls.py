from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from main.views import HomeView


app_name = 'main'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

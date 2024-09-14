from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from user.views import MyLoginView, UserRegistrationView


app_name = 'user'

urlpatterns = [
    path('login/', MyLoginView.as_view(), name='login'),
    path('registration/', UserRegistrationView.as_view(), name='registration'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from user.views import MyLoginView, RegistrationView


urlpatterns = [
    path('login/', MyLoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='registration'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

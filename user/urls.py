from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from user.views import (
    MyLoginView,
    PasswordResetConfirmView,
    PasswordResetFormView,
    ProfileView,
    UserRegistrationView,
    logout_user,
)

from .views import confirm_email_change


app_name = 'user'

urlpatterns = [
    path('login/', MyLoginView.as_view(), name='login'),
    path('registration/', UserRegistrationView.as_view(), name='registration'),
    path('password_reset', PasswordResetFormView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('logout/', logout_user, name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path(
        'confirm-email-change/<uidb64>/<token>/<new_email_encoded>/',
        confirm_email_change,
        name='confirm_email_change',
    ),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

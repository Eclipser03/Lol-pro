from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from user.views import (
    MyLoginView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetFormView,
    UserRegistrationView,
    logout_user,
)


app_name = 'user'

urlpatterns = [
    path('login/', MyLoginView.as_view(), name='login'),
    path('registration/', UserRegistrationView.as_view(), name='registration'),
    path('password_reset', PasswordResetFormView.as_view(), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path(
        'password-reset/complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'
    ),
    path('logout/', logout_user, name='logout'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

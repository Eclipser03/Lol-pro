from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from user.forms import (
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    ProfileChangePasswordForm,
    UserLoginForm,
    UserRegistrationForm,
)
from user.utils import RedirectAuthUser


User = get_user_model()
# Create your views here.


class MyLoginView(RedirectAuthUser, LoginView):
    model = User
    form_class = UserLoginForm
    template_name = 'user/login.html'
    success_url = reverse_lazy('user:registration')


class UserRegistrationView(RedirectAuthUser, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'user/registration.html'
    success_url = reverse_lazy('user:login')
    auth_redirect_link = '/'


class PasswordResetFormView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'user/password_reset_form.html'
    success_url = '/password-reset/done/'
    email_template_name = 'user/password_reset_email.html'


class PasswordResetDoneView(TemplateView):
    template_name = 'user/password_reset_done.html'


class PasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'user/password_reset_confirm.html'
    success_url = reverse_lazy('user:password_reset_complete')


class PasswordResetCompleteView(TemplateView):
    template_name = 'user/password_reset_complete.html'


@login_required
def logout_user(request):
    logout(request)
    return redirect('main:home')


class ProfileView(LoginRequiredMixin, PasswordChangeView):
    form_class = ProfileChangePasswordForm
    template_name = 'user/profile.html'
    success_url = reverse_lazy('user:profile')




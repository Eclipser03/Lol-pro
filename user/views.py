from copy import copy

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.forms import model_to_dict
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import CreateView

from user.forms import (
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    ProfileChangePasswordForm,
    ProfileUpdateForm,
    UpdateUserEmail,
    UserLoginForm,
    UserRegistrationForm,
)
from user.utils import RedirectAuthUser


User = get_user_model()


# Вход в аккаунт
class MyLoginView(RedirectAuthUser, LoginView):
    model = User
    form_class = UserLoginForm
    template_name = 'user/login.html'


# Регистрация пользователя
class UserRegistrationView(RedirectAuthUser, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'user/registration.html'
    success_url = reverse_lazy('user:login')
    auth_redirect_link = '/'


# Забыли пароль
class PasswordResetFormView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'user/password_reset_form.html'
    success_url = '/'
    email_template_name = 'user/password_reset_email.html'

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(request, 'Письмо с инструкцией отправлено на Вашу почту!')
        return response


# Восстановление пароля(забыл папроль)
class PasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'user/password_reset_confirm.html'
    success_url = reverse_lazy('user:login')

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(request, 'Пароль успешно изменен!')
        return response


# Выход из аккаунта
@login_required
def logout_user(request):
    logout(request)
    return redirect('main:home')


# Сохранение значения дискорда,аватарки, никнейма в POST
def FORM_FILL(post, obj):
    """Updates request's POST dictionary with values from object, for update purposes"""
    post = copy(post)
    for k, v in model_to_dict(obj).items():
        if k not in post:
            post[k] = v
    return post


# Смена аватарки, никнейма, дискорда, пароля, почты
class ProfileView(LoginRequiredMixin, PasswordChangeView):
    form_class = ProfileChangePasswordForm
    template_name = 'user/profile.html'
    success_url = reverse_lazy('user:profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_form'] = ProfileUpdateForm(instance=self.request.user)
        context['update_email'] = UpdateUserEmail()
        return context

    def post(self, request, *args, **kwargs):
        if 'update_profile' in request.POST:
            print(request.POST)
            profile_form = ProfileUpdateForm(
                FORM_FILL(request.POST, request.user), request.FILES, instance=request.user
            )

            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Данные успешно обновлены!')
                return redirect('user:profile')

        if 'update_email' in request.POST:
            update_email = UpdateUserEmail(request.POST)
            if update_email.is_valid():
                new_email = update_email.cleaned_data.get('new_email')
                # Отправляем письмо с подтверждением
                self.send_confirmation_email(request, new_email)
                messages.success(request, 'Письмо отправлено на Вашу почту!')
                return redirect('user:profile')
            else:
                errors = update_email.errors.values()
                for error in errors:
                    for text in error:
                        messages.error(request, text)
                return redirect('user:profile')
        if 'update_password' in request.POST:
            form = self.get_form()
            print(form)
            if form.is_valid():
                print(1)
                return self.form_valid(form)

            print(form.errors)
            return self.form_invalid(form)

    # Отправка письма
    def send_confirmation_email(self, request, new_email):
        user = request.user
        new_email_encoded = urlsafe_base64_encode(force_bytes(new_email))
        current_site = get_current_site(request)
        mail_subject = 'Подтверждение изменения электронной почты'
        message = render_to_string(
            'user/confirm_email_change.html',
            {
                'user': user,
                'new_email': new_email_encoded,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token_generator.make_token(user),
            },
        )
        send_mail(mail_subject, message, settings.EMAIL_HOST_USER, [user.email])


# Смена почты
def confirm_email_change(request, uidb64, token, new_email_encoded):
    try:
        new_email = uid = force_str(urlsafe_base64_decode(new_email_encoded))
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and token_generator.check_token(user, token):
        user.email = new_email  # Меняем почту на новую
        user.save()
        messages.success(request, 'Ваша почта успешно обновлена!')
        return redirect('user:profile')
    else:
        messages.error(request, 'Ссылка недействительна или устарела.')
        return redirect('user:profile')

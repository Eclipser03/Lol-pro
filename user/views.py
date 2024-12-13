from copy import copy

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Count, Q
from django.forms import BaseForm, BaseModelForm, model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import CreateView, TemplateView

from main.views import TitleMixin
from store.models import AccountOrder, BoostOrder, ChatRoom, Qualification, RPorder, SkinsOrder
from user.forms import (
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    ProfileChangePasswordForm,
    ProfileUpdateForm,
    UpdateBalanceUser,
    UpdateUserEmail,
    UserLoginForm,
    UserRegistrationForm,
)
from user.tasks import send_email_task
from user.utils import RedirectAuthUser


User = get_user_model()


# Вход в аккаунт
class MyLoginView(TitleMixin, RedirectAuthUser, LoginView):
    model = User
    form_class = UserLoginForm
    template_name = 'user/login.html'
    title = 'Вход в личный кабинет'

    def form_valid(self, form):
        checkbox = form.cleaned_data.get('checkbox')
        print(checkbox)
        if checkbox:
            # Устанавливаем срок жизни сессии на, например, 30 дней
            self.request.session.set_expiry(60 * 60 * 24 * 30)  # 30 дней
        else:
            # Сессия будет закрыта после закрытия браузера
            self.request.session.set_expiry(0)

        return super().form_valid(form)


# Регистрация пользователя
class UserRegistrationView(TitleMixin, SuccessMessageMixin, RedirectAuthUser, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'user/registration.html'
    success_url = reverse_lazy('user:login')
    auth_redirect_link = '/'
    title = 'Регистрация'

    def form_valid(self, form: BaseForm) -> HttpResponse:
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f'Добро пожаловать {user.username}')
        return redirect('/')

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        errors = form.errors.values()
        for error in errors:
            for text in error:
                messages.error(self.request, text)
        return super().form_invalid(form)


# Забыли пароль
class PasswordResetFormView(TitleMixin, PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'user/password_reset_form.html'
    success_url = '/'
    email_template_name = 'user/password_reset_email.html'
    title = 'Восстановление пароля'

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(request, 'Письмо с инструкцией отправлено на Вашу почту!')
        return response


# Восстановление пароля(забыл папроль)
class PasswordResetConfirmView(TitleMixin, PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'user/password_reset_confirm.html'
    success_url = reverse_lazy('user:login')
    title = 'Восстановление пароля'

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


# Смена аватарки, никнейма, дискорда, пароля, почты, пополнение баланса
class ProfileView(TitleMixin, LoginRequiredMixin, PasswordChangeView):
    form_class = ProfileChangePasswordForm
    template_name = 'user/profile.html'
    success_url = reverse_lazy('user:profile')
    title = 'Профиль'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_form'] = ProfileUpdateForm(instance=self.request.user)
        context['update_email'] = UpdateUserEmail()
        context['update_balance'] = UpdateBalanceUser()
        context['boostorders'] = BoostOrder.objects.filter(user=self.request.user).order_by(
            '-created_at'
        )
        all_products = (
            list(Qualification.objects.filter(user=self.request.user))
            + list(SkinsOrder.objects.filter(user=self.request.user))
            + list(RPorder.objects.filter(user=self.request.user))
            + list(AccountOrder.objects.filter(user=self.request.user))
        )
        all_products = sorted(all_products, key=lambda product: product.created_at, reverse=True)
        context['all_products'] = all_products
        return context

    def post(self, request, *args, **kwargs):
        if 'update_balance' in request.POST:
            update_balance_form = UpdateBalanceUser(request.POST)
            if update_balance_form.is_valid():
                request.user.balance += update_balance_form.cleaned_data['balance']
                request.user.save()
                messages.success(request, 'Баланс успешно пополнен!')
            else:
                errors = update_balance_form.errors.values()
                for error in errors:
                    for text in error:
                        messages.error(request, text)
                return redirect('user:profile')
            return redirect('user:profile')

        if 'update_profile' in request.POST:
            print(request.POST)
            profile_form = ProfileUpdateForm(
                FORM_FILL(request.POST, request.user), request.FILES, instance=request.user
            )

            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Данные успешно обновлены!')
                return redirect('user:profile')
            else:
                errors = profile_form.errors.values()
                for error in errors:
                    for text in error:
                        messages.error(request, text)
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
            form.instance = request.user
            if form.is_valid():
                messages.success(request, 'Пароль успешно изменен')
                return self.form_valid(form)

            errors = form.errors.values()
            for error in errors:
                for text in error:
                    messages.error(request, text)
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
        send_email_task.delay(mail_subject, message, [user.email])
        # send_mail(mail_subject, message, settings.EMAIL_HOST_USER, [user.email])


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


class MessagesView(TitleMixin, TemplateView):
    template_name = 'user/messages.html'
    title = 'Сообщения'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chats'] = sorted(
            ChatRoom.objects.annotate(count_messages=Count('messages')).filter(
                Q(seller=self.request.user) | Q(buyer=self.request.user),
                count_messages__gt=0,
            ),
            key=lambda chat: chat.messages.last().created,
            reverse=True,
        )
        chat_id = self.request.GET.get('chat_id')

        if chat_id:
            selected_chat = get_object_or_404(
                ChatRoom, Q(seller=self.request.user) | Q(buyer=self.request.user), id=chat_id
            )

            context['selected_chat'] = selected_chat
            print('123123', selected_chat.account)
        return context


class LicenseAgreementView(TitleMixin, TemplateView):
    template_name = 'user/license_agreement.html'
    title = 'Соглашение'

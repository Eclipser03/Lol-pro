import logging
from itertools import chain

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
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, OuterRef, Prefetch, Subquery
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.generic import CreateView, TemplateView

from store.models import AccountOrder, BoostOrder, ChatRoom, Message, Qualification, RPorder, SkinsOrder
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
from user.utils import RedirectAuthUser
from utils.mixins import TitleMixin
from utils.services import form_fill, handle_form_errors, send_confirmation_email


logger = logging.getLogger('main')
User = get_user_model()


class MyLoginView(TitleMixin, RedirectAuthUser, LoginView):
    model = User
    form_class = UserLoginForm
    template_name = 'user/login.html'
    title = 'Вход в личный кабинет'

    def form_valid(self, form):
        checkbox = form.cleaned_data.get('checkbox')
        if checkbox:
            self.request.session.set_expiry(60 * 60 * 24 * 30)  # 30 дней
        else:
            self.request.session.set_expiry(0)

        return super().form_valid(form)

    def form_invalid(self, form):
        handle_form_errors(self.request, form)
        return super().form_invalid(form)


class UserRegistrationView(TitleMixin, SuccessMessageMixin, RedirectAuthUser, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'user/registration.html'
    success_url = reverse_lazy('user:login')
    title = 'Регистрация'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        logger.info(f'Создан аккаунт {user.username}')
        messages.success(self.request, f'Добро пожаловать {user.username}')
        return redirect('main:home')

    def form_invalid(self, form):
        handle_form_errors(self.request, form)
        return super().form_invalid(form)


class PasswordResetFormView(TitleMixin, PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'user/password_reset_form.html'
    success_url = reverse_lazy('user:login')
    email_template_name = 'user/password_reset_email.html'
    title = 'Восстановление пароля'
    success_message = 'Письмо с инструкцией отправлено на Вашу почту!'

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        logger.info(f'Пользователь c email: {email} запросил восстановление пароля')

        return super().post(request, *args, **kwargs)


class PasswordResetConfirmView(TitleMixin, PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'user/password_reset_confirm.html'
    success_url = reverse_lazy('user:login')
    title = 'Восстановление пароля'
    success_message = 'Пароль успешно изменен!'

    def form_valid(self, form):
        user = form.user
        logger.info(f'Пользователь {user.email} успешно сменил пароль.')
        return super().form_valid(form)


@login_required
def logout_user(request):
    user = request.user
    logger.info(f'Пользователь {user.username} вышел из системы.')
    messages.success(request, 'Вы успешно вышли из системы.')
    logout(request)
    return redirect('main:home')


class ProfileView(TitleMixin, LoginRequiredMixin, PasswordChangeView):
    form_class = ProfileChangePasswordForm
    template_name = 'user/profile.html'
    success_url = reverse_lazy('user:profile')
    title = 'Профиль'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            # ТЫК
            {
                'profile_form': ProfileUpdateForm(instance=self.request.user),
                'update_email': UpdateUserEmail(),
                'update_balance': UpdateBalanceUser(),
                'boostorders': BoostOrder.objects.filter(user=self.request.user)
                .select_related('user', 'coupon_code')
                .order_by('-created_at'),
                'all_products': sorted(
                    chain(
                        Qualification.objects.filter(user=self.request.user).select_related(
                            'user', 'coupon_code'
                        ),
                        SkinsOrder.objects.filter(user=self.request.user).select_related('user'),
                        RPorder.objects.filter(user=self.request.user).select_related('user'),
                        AccountOrder.objects.filter(user=self.request.user).select_related(
                            'user', 'account'
                        ),
                    ),
                    key=lambda product: product.created_at,
                    reverse=True,
                ),
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        logger.info(f'Запрос на обновление профиля пользователя {request.user.username}')

        form_handlers = {
            'update_balance': self.handle_update_balance,
            'update_profile': self.handle_update_profile,
            'update_email': self.handle_update_email,
            'update_password': self.handle_update_password,
        }

        for key, handler in form_handlers.items():
            if key in request.POST:
                return handler(request)

        messages.error(request, 'Некорректный запрос.')
        return redirect('user:profile')

    def handle_update_balance(self, request):
        form = UpdateBalanceUser(request.POST)

        if form.is_valid():
            logger.info(f'Баланс пользователя {request.user.username} был обновлён')
            request.user.balance += form.cleaned_data['balance']
            request.user.save()
            messages.success(request, 'Баланс успешно пополнен!')
        else:
            handle_form_errors(request, form)

        return redirect('user:profile')

    def handle_update_profile(self, request):
        form = ProfileUpdateForm(
            form_fill(request.POST, request.user), request.FILES, instance=request.user
        )

        if form.is_valid():
            form.save()
            logger.info(f'Профиль пользователя {request.user.username} успешно обновлён.')
            messages.success(request, 'Данные успешно обновлены!')
        else:
            handle_form_errors(request, form)

        return redirect('user:profile')

    def handle_update_email(self, request):
        form = UpdateUserEmail(request.POST)

        if form.is_valid():
            new_email = form.cleaned_data.get('new_email')
            send_confirmation_email(request.user, request, new_email)
            logger.info(f'Письмо для изменения email отправлено пользователю {request.user.username}.')
            messages.success(request, 'Письмо отправлено на Вашу почту!')
        else:
            handle_form_errors(request, form)
        return redirect('user:profile')

    def handle_update_password(self, request):
        form = self.get_form()
        form.instance = request.user

        if form.is_valid():
            logger.info(f'Пользователь {request.user.username} успешно изменил пароль.')
            messages.success(request, 'Пароль успешно изменен')
            return self.form_valid(form)

        handle_form_errors(request, form)
        return self.form_invalid(form)


def confirm_email_change(request, uidb64, token, new_email_encoded):
    try:
        new_email = force_str(urlsafe_base64_decode(new_email_encoded))
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None

    if user and token_generator.check_token(user, token):
        user.email = new_email
        user.save()
        messages.success(request, 'Ваша почта успешно обновлена!')
        return redirect('user:profile')

    messages.error(request, 'Ссылка недействительна или устарела.')
    return redirect('user:profile')


class MessagesView(TitleMixin, TemplateView):
    template_name = 'user/messages.html'
    title = 'Сообщения'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ТЫК
        context['chats'] = (
            ChatRoom.objects.select_related('buyer', 'seller', 'account')
            .prefetch_related(
                Prefetch(
                    'messages',
                    queryset=Message.objects.filter(
                        id__in=Subquery(
                            ChatRoom.objects.annotate(
                                last_message=Subquery(
                                    Message.objects.filter(chat_room_id=OuterRef('id'))
                                    .order_by('-id')
                                    .values_list('id', flat=True)[:1]
                                )
                            ).values_list('last_message', flat=True)
                        )
                    ).select_related('author'),
                ),
            )
            .filter(
                Q(seller=self.request.user) | Q(buyer=self.request.user),
                messages__isnull=False,
            )
            .distinct()
        )

        chat_id = self.request.GET.get('chat_id')

        if chat_id:
            context['selected_chat'] = get_object_or_404(
                ChatRoom.objects.select_related('buyer', 'seller', 'account').prefetch_related(
                    'messages', 'messages__author'
                ),
                Q(seller=self.request.user) | Q(buyer=self.request.user),
                id=chat_id,
            )

        return context


class LicenseAgreementView(TitleMixin, TemplateView):
    template_name = 'user/license_agreement.html'
    title = 'Соглашение'

import logging
from collections.abc import Callable

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django_recaptcha.fields import ReCaptchaField

from lol_pay.celery import app


logger = logging.getLogger('django.contrib.auth')

User = get_user_model()


def password_reset_send_mail_override(func: Callable) -> Callable:
    def wrap(*args, **kwargs):
        args = list(args)

        args[0] = 'CustomPasswordResetForm'
        args[3]['username'] = args[3]['user'].get_username()
        args[4] = settings.EMAIL_HOST_USER
        del args[3]['user']
        func.delay(*args, **kwargs)

    return wrap


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'login_input', 'placeholder': 'Логин'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'password_input', 'placeholder': 'Пароль'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'password_input', 'placeholder': 'Подтвердите пароль'}
        )
    )
    email = forms.CharField(widget=forms.EmailInput(attrs={'name': 'email', 'placeholder': 'Почта'}))
    checkbox = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'name': 'Я соглашаюсь'}), label='Я соглашаюсь', required=True
    )
    captcha = ReCaptchaField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'captcha')


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'login_input', 'placeholder': 'Логин'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'password_input', 'placeholder': 'Пароль'})
    )
    checkbox = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'name': 'Запомнить меня'}),
        label='Запомнить меня',
        required=False,
    )

    class Meta:
        model = User
        fields = ('username', 'password')


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'password_input', 'placeholder': 'Пароль'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'password_input', 'placeholder': 'Подтвердите пароль'}
        )
    )


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'name': 'email', 'placeholder': 'Введите адрес почты'})
    )

    @password_reset_send_mail_override
    @app.task
    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()


class ProfileChangePasswordForm(SetPasswordForm):
    old_password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'current-password',
                'autofocus': True,
                'placeholder': 'Текущий пароль',
                'class': 'oldpassword',
            }
        ),
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'password_input', 'placeholder': 'Новый пароль'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'password_input', 'placeholder': 'Подтвердите пароль'}
        )
    )

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']

        if not self.instance.check_password(old_password):
            raise forms.ValidationError('Неправильно введен текущий пароль')

        return old_password

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')


class ProfileUpdateForm(forms.ModelForm):
    game_username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Никнейм'}), required=False
    )
    discord = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Discord никнейм'}), required=False
    )

    avatar = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'file-input', 'onchange': 'uploadAvatar()'}),
        required=False,
    )

    class Meta:
        model = User
        fields = ('game_username', 'discord', 'avatar')


class UpdateUserEmail(forms.Form):
    new_email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Введите новую почту'}))

    def clean_new_email(self):
        new_email = self.cleaned_data['new_email']

        # Проверка, существует ли уже такой email в базе данных
        if User.objects.filter(email=new_email).exists():
            raise forms.ValidationError('Этот email уже используется.')

        return new_email


class UpdateBalanceUser(forms.Form):
    balance = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Введите сумму'}))

    def clean_balance(self):
        if self.cleaned_data['balance'] < 0:
            raise forms.ValidationError('Введите положительную сумму')

        return self.cleaned_data['balance']

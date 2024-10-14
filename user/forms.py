from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django_recaptcha.fields import ReCaptchaField


User = get_user_model()


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

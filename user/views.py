from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from user.forms import UserLoginForm, UserRegistrationForm
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

from django.views.generic import TemplateView


# Create your views here.


class MyLoginView(TemplateView):
    template_name = 'user/login.html'


class RegistrationView(TemplateView):
    template_name = 'user/base.html'

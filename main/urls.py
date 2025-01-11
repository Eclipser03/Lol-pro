from django.urls import path, re_path

from main.views import HomeView, ReviewsView, flower_proxy_view


app_name = 'main'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('reviews/', ReviewsView.as_view(), name='reviews'),
    re_path('flower/(?P<path>.*)', flower_proxy_view, name='flower'),
]

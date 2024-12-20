from django.urls import path

from main.views import HomeView, ReviewsView


app_name = 'main'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('reviews/', ReviewsView.as_view(), name='reviews'),
]

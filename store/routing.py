from django.urls import path

from . import consumers


websocket_urlpatterns = [
    path('ws/chat/<int:room_id>/<int:account_id>/', consumers.ChatConsumer.as_asgi()),
]

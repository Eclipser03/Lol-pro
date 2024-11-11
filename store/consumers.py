import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from user.models import User
from .models import ChatRoom, Message

class ChatConsumer(AsyncWebsocketConsumer):
    pass

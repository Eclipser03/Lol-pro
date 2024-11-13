import json

from channels.generic.websocket import AsyncWebsocketConsumer

from .models import ChatRoom, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        # print('СЕЛФ СКОП---',self.scope, 'USUS', self.room_id)
        self.room_group_name = f'chat_{self.room_id}'

        # Присоединяемся к группе
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Покидаем группу
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Получаем сообщение от WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        chat_room = await ChatRoom.objects.aget(id=self.room_id)
        sms = await self.create_message(chat_room, self.scope['user'], message)
        # Отправляем сообщение в группу
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.scope['user'].username,
                'created': str(sms.created.strftime('%H:%M')),
            },
        )

    # Получаем сообщение от группы
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        created = event['created']

        # Отправляем сообщение обратно клиенту
        await self.send(
            text_data=json.dumps({'message': message, 'username': username, 'created': created})
        )

    async def create_message(self, chat_room, author, text):
        return await Message.objects.acreate(chat_room=chat_room, author=author, text=text)

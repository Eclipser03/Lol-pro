import json

from channels.generic.websocket import AsyncWebsocketConsumer

from user.models import User

from .models import AccountObject, ChatRoom, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.account_id = self.scope['url_route']['kwargs']['account_id']
        self.room_group_name = f'chat_{self.room_id}_{self.account_id}'
        self.chat_room = await ChatRoom.objects.aget(id=self.room_id)
        # Присоединяемся к группе
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Покидаем группу
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Получаем сообщение от WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        # Отправляем сообщение в группу
        if text_data_json['type'] == 'chat_message':
            message = text_data_json['message']
            sms = await self.create_message(self.chat_room, self.scope['user'], message, 'chat_message')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': self.scope['user'].username,
                    'created': str(sms.created.strftime('%H:%M')),
                },
            )
        if text_data_json['type'] == 'buy_account':
            message = f"Пользователь {self.scope['user'].username} купил аккаунт."
            sms = await self.create_message(self.chat_room, self.scope['user'], message, 'buy_account')
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'buy_account', 'userid': self.scope['user'].id, 'message': message},
            )
        if text_data_json['type'] == 'buy_account_acept':
            message = f"Покупка подтверждена пользователем {self.scope['user'].username}."
            sms = await self.create_message(self.chat_room, self.scope['user'], message, 'buy_account_acept')
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'buy_account_acept', 'userid': self.scope['user'].id, 'message': message},
            )

    async def buy_account_acept(self, event):
        userid = event['userid']
        account = await AccountObject.objects.aget(acount_chat_rooms=self.chat_room)
        seller = await User.objects.aget(seller_chat_rooms=self.chat_room)
        message = event['message']
        if not account.is_confirmed:
            seller.balance += account.price
            account.is_confirmed = True
            await seller.asave()
            await account.asave()
        else:
            await self.send(
                text_data=json.dumps({'type': 'error', 'message': 'Ошибка', 'userid': userid})
            )
        await self.send(text_data=json.dumps({'type': 'buy_account_acept', 'message': message}))
        return

    async def buy_account(self, event):
        userid = event['userid']
        user = self.scope['user']
        account = await AccountObject.objects.aget(acount_chat_rooms=self.chat_room)
        if user.balance >= account.price and account.is_active:
            user.balance -= account.price
            await user.asave()
            account.is_active = False
            await account.asave()
            await self.send(
                text_data=json.dumps(
                    {
                        'type': 'buy_account',
                        'userid': userid,
                    }
                )
            )
        else:
            await self.send(
                text_data=json.dumps({'type': 'error', 'message': 'Ошибка', 'userid': userid})
            )
            return

    # Получаем сообщение от группы
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        created = event['created']

        # Отправляем сообщение обратно клиенту
        await self.send(
            text_data=json.dumps(
                {'type': 'chat_message', 'message': message, 'username': username, 'created': created}
            )
        )

    async def create_message(self, chat_room, author, text, massagetype):
        return await Message.objects.acreate(
            chat_room=chat_room, author=author, text=text, massage_type=massagetype
        )

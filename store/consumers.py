import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from user.models import User

from .models import AccountObject, AccountOrder, ChatRoom, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.account_id = self.scope['url_route']['kwargs']['account_id']
        self.room_group_name = f'chat_{self.room_id}_{self.account_id}'
        self.chat_room = await ChatRoom.objects.aget(id=self.room_id)
        self.recipient = (
            self.chat_room.seller_id
            if self.chat_room.seller_id != self.scope['user'].id
            else self.chat_room.buyer_id
        )
        self.account = await AccountObject.objects.aget(acount_chat_rooms=self.chat_room)
        # Присоединяемся к группе
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Покидаем группу
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Получаем сообщение от WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print('text_data_json', text_data_json)

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

            await self.channel_layer.group_send(
                f'user_{self.recipient}',
                {
                    'type': 'send_notification',
                    'message': f'Новое сообщение от {self.scope['user'].username}',
                    'created': str(sms.created.strftime('%H:%M')),
                    'username': self.scope['user'].username,
                    'chat_room': self.chat_room.id,
                },
            )
        elif text_data_json['type'] == 'buy_account':
            message = f"Пользователь {self.scope['user'].username} купил аккаунт."
            sms = await self.create_message(self.chat_room, self.scope['user'], message, 'buy_account')
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'buy_account', 'userid': self.scope['user'].id, 'message': message},
            )

            await self.channel_layer.group_send(
                f'user_{self.recipient}',
                {
                    'type': 'send_notification',
                    'message': f'{self.scope['user'].username} оплатил ваш аккаунт',
                    'created': str(sms.created.strftime('%H:%M')),
                    'username': self.scope['user'].username,
                    'chat_room': self.chat_room.id,
                },
            )
        elif text_data_json['type'] == 'buy_account_cancel':
            seller_username = await sync_to_async(lambda: self.chat_room.seller.username)()
            message = f'Продавец {seller_username} отменил заказ.'
            sms = await self.create_message(
                self.chat_room, self.scope['user'], message, 'buy_account_cancel'
            )
            print('11', self.room_group_name)
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'cancell', 'userid': str(self.scope['user'].id), 'message': message},
            )

            await self.channel_layer.group_send(
                f'user_{self.recipient}',
                {
                    'type': 'send_notification',
                    'message': f'{seller_username} отменил заказ',
                    'created': str(sms.created.strftime('%H:%M')),
                    'username': self.scope['user'].username,
                    'chat_room': self.chat_room.id,
                },
            )
        elif text_data_json['type'] == 'buy_account_acept':
            message = f"Покупка подтверждена пользователем {self.scope['user'].username}."
            sms = await self.create_message(
                self.chat_room, self.scope['user'], message, 'buy_account_acept'
            )
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'buy_account_acept', 'userid': self.scope['user'].id, 'message': message},
            )

            await self.channel_layer.group_send(
                f'user_{self.recipient}',
                {
                    'type': 'send_notification',
                    'message': 'Покупка подтвержден, деньги зачислены на ваш счет',
                    'created': str(sms.created.strftime('%H:%M')),
                    'username': self.scope['user'].username,
                    'chat_room': self.chat_room.id,
                },
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
            data = {'account': account}
            await self.create_record(data)
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

    async def cancell(self, event):
        userid = event['userid']
        if not self.account.is_active:
            buyer = await User.objects.aget(buyer_chat_rooms=self.chat_room)
            buyer.balance += self.account.price
            await buyer.asave()
            self.account.is_active = True
            await self.account.asave()
            await self.send(
                text_data=json.dumps(
                    {
                        'type': 'buy_account_cancel',
                        'userid': userid,
                    }
                )
            )
        else:
            await self.send(
                text_data=json.dumps({'type': 'error', 'message': 'Ошибка', 'userid': userid})
            )

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

    @database_sync_to_async
    def create_record(self, data):
        buyer = self.chat_room.buyer
        return AccountOrder.objects.create(user=buyer, account=data['account'])


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            self.user_group_name = f'user_{self.scope['user'].id}'
            await self.channel_layer.group_add(self.user_group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def send_notification(self, event):
        message1 = event['message']
        created = event['created']
        username = event['username']
        chat_room = event['chat_room']
        print('1321', message1, created, event)
        await self.send(
            text_data=json.dumps(
                {
                    'type': 'notification',
                    'message': message1,
                    'created': created,
                    'username': username,
                    'chat_room': chat_room,
                }
            )
        )

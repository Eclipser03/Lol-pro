import json
from datetime import timedelta

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from user.models import User

from .models import AccountObject, AccountOrder, ChatRoom, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('Scope during connect:', self.scope)
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            print(f'Room ID: {self.room_id}')
        except KeyError:
            print("Error: 'url_route' or 'kwargs' is missing in scope!")
            await self.close()
            return
        self.room_group_name = f'chat_{self.room_id}'
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
            created = sms.created + timedelta(hours=3)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': self.scope['user'].username,
                    'created': str(created.strftime('%H:%M')),
                    'link': f'/messages/?chat_id={self.chat_room.id}',
                },
            )

            await self.channel_layer.group_send(
                f'user_{self.recipient}',
                {
                    'type': 'send_notification',
                    'message': f'Новое сообщение от {self.scope['user'].username}',
                    'message_content': message,
                    'avatar': self.scope['user'].avatar.url,
                    'created': str(created.strftime('%H:%M')),
                    'username': self.scope['user'].username,
                    'chat_room': self.chat_room.id,
                    'link': f'/messages/?chat_id={self.chat_room.id}',
                },
            )
        elif text_data_json['type'] == 'buy_account':
            message = f"Пользователь {self.scope['user'].username} купил аккаунт."
            buyer = await User.objects.aget(buyer_chat_rooms=self.chat_room)
            account = await AccountObject.objects.aget(acount_chat_rooms=self.chat_room)
            if buyer.balance >= account.price and account.is_active:
                sms = await self.create_message(
                    self.chat_room, self.scope['user'], message, 'buy_account'
                )
                buyer.balance -= account.price
                await buyer.asave()
                print('OLA123')
                account.is_active = False
                account.buyer = buyer
                await account.asave()
                print('asdas', account.is_active)
                print('123', buyer.balance)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {'type': 'buy_account', 'userid': self.scope['user'].id, 'message': message},
                )

                await self.channel_layer.group_send(
                    f'user_{self.recipient}',
                    {
                        'type': 'send_notification',
                        'message': f'{self.scope['user'].username} оплатил ваш аккаунт',
                        'message_content': f'{self.scope['user'].username} оплатил ваш аккаунт',
                        'created': str(sms.created.strftime('%H:%M')),
                        'username': self.scope['user'].username,
                        'avatar': self.scope['user'].avatar.url,
                        'chat_room': self.chat_room.id,
                        'link': f'/messages/?chat_id={self.chat_room.id}',
                    },
                )
            else:
                await self.channel_layer.group_send(
                    f'user_{self.chat_room.buyer_id}',
                    {
                        'type': 'send_error',
                        'message': 'Ошибка покупки',
                    },
                )
        elif text_data_json['type'] == 'buy_account_cancel':
            seller_username = await sync_to_async(lambda: self.chat_room.seller.username)()
            message = f'Продавец {seller_username} отменил заказ.'
            sms = await self.create_message(
                self.chat_room, self.scope['user'], message, 'buy_account_cancel'
            )
            account = await AccountObject.objects.aget(id=self.account.id)
            if not account.is_active:
                buyer = await User.objects.aget(buyer_chat_rooms=self.chat_room)
                buyer.balance += account.price
                await buyer.asave()
                account.is_active = True
                account.buyer = None
                await account.asave()
                print(12345)
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
                    'message_content': f'{seller_username} отменил заказ',
                    'created': str(sms.created.strftime('%H:%M')),
                    'username': self.scope['user'].username,
                    'avatar': self.scope['user'].avatar.url,
                    'chat_room': self.chat_room.id,
                    'link': f'/messages/?chat_id={self.chat_room.id}',
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
                    'avatar': self.scope['user'].avatar.url,
                    'chat_room': self.chat_room.id,
                    'link': f'/messages/?chat_id={self.chat_room.id}',
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
        else:
            await self.send(
                text_data=json.dumps({'type': 'error', 'message': 'Ошибка', 'userid': userid})
            )
            return
        await self.send(text_data=json.dumps({'type': 'buy_account_acept', 'message': message}))
        await self.create_record(data)
        return

    async def buy_account(self, event):
        userid = event['userid']

        await self.send(
            text_data=json.dumps(
                {
                    'type': 'buy_account',
                    'userid': userid,
                }
            )
        )

    async def cancell(self, event):
        userid = event['userid']
        await self.send(
            text_data=json.dumps(
                {
                    'type': 'buy_account_cancel',
                    'message': 'Продавец отменил заказ',
                    'userid': userid,
                }
            )
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
        return AccountOrder.objects.get_or_create(user=buyer, account=data['account'])[0]


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            self.user_group_name = f'user_{self.scope['user'].id}'
            print('СРАБОТАЛО')
            await self.channel_layer.group_add(self.user_group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def send_notification(self, event):
        message = event['message']
        message_content = event.get('message_content', '')
        avatar = event.get('avatar', '')
        created = event['created']
        username = event['username']
        chat_room = event['chat_room']
        link = event['link']
        await self.send(
            text_data=json.dumps(
                {
                    'type': 'notification',
                    'message': message,
                    'message_content': message_content,
                    'created': created,
                    'username': username,
                    'chat_room': chat_room,
                    'link': link,
                    'avatar': avatar,
                }
            )
        )

    async def send_error(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    'type': 'error',
                    'message': event['message'],
                }
            )
        )

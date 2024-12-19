import json
import os
from http import HTTPStatus

from channels.db import database_sync_to_async
from channels.testing import ChannelsLiveServerTestCase, WebsocketCommunicator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from store.consumers import ChatConsumer, NotificationConsumer
from store.models import AccountObject, AccountOrder, ChatRoom, Coupon, ReviewSellerModel
from store.services import calculate_boost, calculate_qualification
from user.models import User


class StoreTestCase(TestCase):
    @classmethod
    def setUp(cls):
        cls.user1_username = cls.user1_password = 'user1'
        cls.user1_email = 'user1@yandex.ru'

        cls.user1 = User.objects.create_user(cls.user1_username, cls.user1_email, cls.user1_password)
        cls.user1.balance = 100000
        cls.user1.save()

        cls.user2_username = cls.user2_password = 'user2'
        cls.user2_email = 'user2@yandex.ru'
        cls.user2 = User.objects.create_user(cls.user2_username, cls.user2_email, cls.user2_password)

    def test_store_page(self):
        path = reverse('store:store')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Добро пожаловать на Lol-pay', response.content.decode())
        self.assertIn('Скины', response.content.decode())
        self.assertIn('RP', response.content.decode())
        self.assertIn('Персонажи', response.content.decode())
        self.assertIn('Аккаунты', response.content.decode())
        self.assertIn('Буст', response.content.decode())

    def test_rp_page(self):
        path = reverse('store:store_rp')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Купить RP', response.content.decode())

    def test_rp_purchase(self):
        self.client.login(username=self.user1_username, password=self.user1_password)
        path = reverse('store:store_rp')
        self.assertEqual(self.user1.balance, 100000)
        self.assertEqual(self.user1.rp_orders.all().count(), 0)
        response = self.client.post(
            path,
            {'rp': 1000, 'server': 'EU WEST', 'account_name': 'test', 'user': self.user1},
            follow=True,
        )
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.balance, 99770)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.user1.rp_orders.all().count(), 1)

    def test_rp_purchase_error(self):
        self.client.login(username=self.user1_username, password=self.user1_password)
        path = reverse('store:store_rp')
        self.assertEqual(self.user1.balance, 100000)
        self.assertEqual(self.user1.rp_orders.all().count(), 0)
        response = self.client.post(
            path,
            {'rp': 434791, 'server': 'EU WEST', 'account_name': 'test', 'user': self.user1},
            follow=True,
        )
        self.user1.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Пополните баланс', response.content.decode())

    def test_skin_char_page(self):
        path = reverse('store:store_skins')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Купить персонажа или скин:', response.content.decode())

    def test_skin_purchase(self):
        self.client.login(username=self.user1_username, password=self.user1_password)
        path = reverse('store:store_skins')
        self.assertEqual(self.user1.balance, 100000)
        self.assertEqual(self.user1.skins_orders.all().count(), 0)
        response = self.client.post(
            path,
            {
                'server': 'EU WEST',
                'account_name': 'test',
                'user': self.user1,
                'char_name': '',
                'skin_name': 'Галактический Азир',
                'price_char': '',
                'price_skin': '',
            },
            follow=True,
        )
        json_path = os.path.join(settings.BASE_DIR, 'static', 'chars', 'assets', 'skins2price.json')
        with open(json_path, encoding='utf-8') as file:
            json_data = json.load(file)
        price = json_data['Галактический Азир']

        self.user1.refresh_from_db()
        self.assertEqual(self.user1.balance, 100000 - price)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.user1.skins_orders.all().count(), 1)

    def test_skin_purchase_error(self):
        self.client.login(username=self.user1_username, password=self.user1_password)
        path = reverse('store:store_skins')
        self.assertEqual(self.user1.balance, 100000)
        self.assertEqual(self.user1.skins_orders.all().count(), 0)
        response = self.client.post(
            path,
            {
                'server': 'EU WEST',
                'account_name': '',
                'user': self.user1,
                'char_name': '',
                'skin_name': 'Галактический Азир',
                'price_char': '',
                'price_skin': '',
            },
            follow=True,
        )
        json_path = os.path.join(settings.BASE_DIR, 'static', 'chars', 'assets', 'skins2price.json')
        with open(json_path, encoding='utf-8') as file:
            json_data = json.load(file)
        price = json_data['Галактический Азир']
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Обязательное поле.', response.content.decode())

    def test_char_purchase(self):
        self.client.login(username=self.user1_username, password=self.user1_password)
        path = reverse('store:store_skins')
        self.assertEqual(self.user1.balance, 100000)
        self.assertEqual(self.user1.skins_orders.all().count(), 0)
        response = self.client.post(
            path,
            {
                'server': 'EU WEST',
                'account_name': 'test',
                'user': self.user1,
                'char_name': 'Азир',
                'skin_name': '',
                'price_char': '',
                'price_skin': '',
            },
            follow=True,
        )
        json_path = os.path.join(settings.BASE_DIR, 'static', 'chars', 'assets', 'name2price.json')
        with open(json_path, encoding='utf-8') as file:
            json_data = json.load(file)
        price = json_data['Азир']
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.balance, 100000 - price)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.user1.skins_orders.all().count(), 1)

    def test_elo_boost_page(self):
        path = reverse('store:store_elo_boost')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Купить пакет эло буста', response.content.decode())
        self.assertIn('ЗОЛОТОЙ', response.content.decode())
        self.assertIn('ПЛАТИНОВЫЙ', response.content.decode())
        self.assertIn('ИЗУМРУДНЫЙ', response.content.decode())
        self.assertIn('АЛМАЗНЫЙ', response.content.decode())
        self.assertIn('Отборочные игры', response.content.decode())

    def test_elo_boost_choise_page(self):
        path = reverse('store:store_elo_boost_choice')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('ТЕКУЩАЯ ПОЗИЦИЯ', response.content.decode())
        self.assertIn('ЖЕЛАЕМАЯ ПОЗИЦИЯ', response.content.decode())
        self.assertIn('КУПИТЬ', response.content.decode())

    def test_elo_boost_purchase(self):
        data = {
            'user': self.user1,
            'current_position': '2',  # SILVER
            'current_division': '1',  # DIVISION 2
            'current_lp': '1',  # 21-40LP
            'desired_position': '3',  # GOLD
            'desired_division': '3',  # DIVISION 4
            'lp_per_win': '1',  # 18+LP
            'server': '1',  # EU WEST
            'queue_type': '0',  # SOLO/DUO
            'specific_role': False,  # Определенная роль не выбрана
            'duo_booster': False,  # Дуо-услуга не выбрана
            'total_time': '00:10:00',  # Время исполнения (10 минут)
            'total_price': 1000,
        }
        self.client.login(username=self.user1_username, password=self.user1_password)
        path = reverse('store:store_elo_boost_choice')
        self.assertEqual(self.user1.balance, 100000)
        self.assertEqual(self.user1.boost_orders.all().count(), 0)
        response = self.client.post(
            path,
            data,
            follow=True,
        )
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.balance, 100000 - calculate_boost(data))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.user1.boost_orders.all().count(), 1)

    def test_elo_boost_purchase_error(self):
        data = {
            'user': self.user1,
            'current_position': '2',  # SILVER
            'current_division': '1',  # DIVISION 2
            'current_lp': '1',  # 21-40LP
            'desired_position': '1',  # GOLD
            'desired_division': '3',  # DIVISION 4
            'lp_per_win': '1',  # 18+LP
            'server': '1',  # EU WEST
            'queue_type': '0',  # SOLO/DUO
            'specific_role': False,  # Определенная роль не выбрана
            'duo_booster': False,  # Дуо-услуга не выбрана
            'total_time': '00:10:00',  # Время исполнения (10 минут)
            'total_price': 1000,
        }
        self.client.login(username=self.user1_username, password=self.user1_password)
        path = reverse('store:store_elo_boost_choice')
        self.assertEqual(self.user1.balance, 100000)
        self.assertEqual(self.user1.boost_orders.all().count(), 0)
        response = self.client.post(
            path,
            data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Текущая позиция не может быть больше желаемой', response.content.decode())

    def test_placement_matches_page(self):
        path = reverse('store:placement_matches')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('РАНГ В ПРОШЛОМ СПЛИТЕ', response.content.decode())
        self.assertIn('КОЛИЧЕСТВО ИГР', response.content.decode())
        self.assertIn('КУПИТЬ', response.content.decode())

    def test_placement_matches_purchase(self):
        data = {
            'user': self.user1,
            'previous_position': '2',  # SILVER
            'server': '1',  # EU WEST
            'game_count': '5',
            'queue_type': '0',  # SOLO/DUO
            'specific_role': False,  # Определенная роль не выбрана
            'duo_booster': False,  # Дуо-услуга не выбрана
            'total_time': '00:10:00',  # Время исполнения (10 минут)
            'total_price': 800,  # Цена (300)
        }
        self.client.login(username=self.user1_username, password=self.user1_password)
        path = reverse('store:placement_matches')
        self.assertEqual(self.user1.balance, 100000)
        self.assertEqual(self.user1.qualification_orders.all().count(), 0)
        response = self.client.post(
            path,
            data,
            follow=True,
        )
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.balance, 100000 - calculate_qualification(data))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.user1.qualification_orders.all().count(), 1)

    def test_placement_matches_purchase_coupon(self):
        coupon = Coupon.objects.create(
            name='test', sale=20, is_active=True, end_date='2025-10-10', count=200
        )
        coupon1 = Coupon.objects.create(
            name='test1', sale=10, is_active=True, end_date='2025-10-10', count=200
        )
        coupon.save()
        print('fafa', Coupon.objects.all().count())
        data = {
            'user': self.user1,
            'previous_position': '2',  # SILVER
            'server': '1',  # EU WEST
            'game_count': '5',
            'queue_type': '0',  # SOLO/DUO
            'specific_role': False,  # Определенная роль не выбрана
            'duo_booster': False,  # Дуо-услуга не выбрана
            'total_time': 10,  # Время исполнения (10 минут)
            'total_price': 640,  # Цена (300)
            'coupon_code': 'test',
        }
        self.client.login(username=self.user1_username, password=self.user1_password)
        path = reverse('store:placement_matches')
        self.assertEqual(self.user1.balance, 100000)
        self.assertEqual(self.user1.qualification_orders.all().count(), 0)
        response = self.client.post(
            path,
            data,
            follow=True,
        )
        data['coupon_code'] = coupon
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.balance, 100000 - calculate_qualification(data))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.user1.qualification_orders.all().count(), 1)
        coupon.refresh_from_db()
        data['coupon_code'] = 'test'
        response = self.client.post(
            path,
            data,
            follow=True,
        )
        print(response.content.decode())
        print(self.user1.qualification_orders.last().coupon_code)
        self.assertEqual(self.user1.qualification_orders.all().count(), 1)

        path = reverse('store:check-coupon')
        response = self.client.post(path, json.dumps({'coupon': 'test1'}), content_type='application/json')

        self.assertTrue(response.json()['success'])
        self.assertEqual(response.json()['message'], 'Купон успешно применен')
        self.assertEqual(response.json()['discount'], 10)
        response = self.client.post(path, json.dumps({'coupon': 'test2'}), content_type='application/json')
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['message'], 'Купон не найден')
        self.assertEqual(response.json()['discount'], 0)
        response = self.client.post(path, json.dumps({'coupon': 'test'}), content_type='application/json')
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['message'], 'Купон уже был использован')
        self.assertEqual(response.json()['discount'], 0)

    def test_accounts_page(self):
        path = reverse('store:store_accounts')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Добавить аккаунт', response.content.decode())
        self.assertIn('Применить фильтры', response.content.decode())

    def test_accounts_add_account(self):
        self.client.login(username=self.user1_username, password=self.user1_password)
        self.assertEqual(self.user1.acounts_objects.all().count(), 0)
        path = reverse('store:store_accounts')
        response = self.client.post(
            path,
            {
                'user': self.user1,
                'server': 'EU WEST',
                'lvl': 11,
                'champions': 11,
                'skins': 11,
                'rang': 'IRON',
                'short_description': 'test',
                'description': 'test',
                'price': 1000,
            },
            follow=True,
        )
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.acounts_objects.all().count(), 1)
        self.assertFalse(self.user1.acounts_objects.last().is_active)
        account = self.user1.acounts_objects.last()
        account.is_active = True
        account.save()
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(self.user1.acounts_objects.last().is_active)
        self.assertIn('Добавить аккаунт', response.content.decode())
        self.assertIn('Применить фильтры', response.content.decode())
        self.assertIn('Мои аккаунты', response.content.decode())
        self.assertIn('EU WEST', response.content.decode())
        self.assertIn('1000', response.content.decode())

    def test_accounts_filters(self):
        self.client.login(username=self.user1_username, password=self.user1_password)
        self.assertEqual(self.user1.acounts_objects.all().count(), 0)
        path = reverse('store:store_accounts')
        response = self.client.post(
            path,
            {
                'user': self.user1,
                'server': 'EU WEST',
                'lvl': 11,
                'champions': 11,
                'skins': 11,
                'rang': 'IRON',
                'short_description': 'test',
                'description': 'test',
                'price': 100,
            },
            follow=True,
        )
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.acounts_objects.all().count(), 1)
        self.assertFalse(self.user1.acounts_objects.last().is_active)
        account = self.user1.acounts_objects.last()
        account.is_active = True
        account.save()
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(self.user1.acounts_objects.last().is_active)
        self.assertIn('test', response.content.decode())
        print(response.content.decode())
        response = self.client.get(
            path,
            {
                'price_min': 1001,
                'price_max': '',
                'champions_min': '',
                'champions_max': '',
                'server': '',
                'rank': '',
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn('test', response.content.decode())

    def test_account_page(self):
        self.client.login(username=self.user1_username, password=self.user1_password)
        path = reverse('store:store_accounts')
        response = self.client.post(
            path,
            {
                'user': self.user1,
                'server': 'EU WEST',
                'lvl': 11,
                'champions': 11,
                'skins': 11,
                'rang': 'IRON',
                'short_description': 'test',
                'description': 'test',
                'price': 1000,
            },
            follow=True,
        )
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.acounts_objects.all().count(), 1)
        self.assertFalse(self.user1.acounts_objects.last().is_active)
        account = self.user1.acounts_objects.last()
        account.is_active = True
        account.save()
        path = reverse('store:store_account_page', kwargs={'id': account.id})
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Оформление заказа', response.content.decode())
        self.assertIn('Отзывы о продавце', response.content.decode())
        self.assertIn('Цена аккаунта:', response.content.decode())
        self.assertIn('Редактировать', response.content.decode())
        self.assertIn('Удалить аккаунт', response.content.decode())
        self.assertIn('EU WEST', response.content.decode())

        image_path1 = os.path.join(settings.MEDIA_ROOT, 'avatar.jpg')
        image_path2 = os.path.join(settings.MEDIA_ROOT, 'diamond_bundle.jpg')
        if os.path.exists(image_path1):
            # Открываем изображение и создаем SimpleUploadedFile
            with open(image_path1, 'rb') as image_file:
                image_file1 = SimpleUploadedFile(
                    name='avatar.jpg', content=image_file.read(), content_type='image/jpeg'
                )
        if os.path.exists(image_path2):
            # Открываем изображение и создаем SimpleUploadedFile
            with open(image_path2, 'rb') as image_file:
                image_file2 = SimpleUploadedFile(
                    name='diamond_bundle.jpg', content=image_file.read(), content_type='image/jpeg'
                )

        response = self.client.post(
            path,
            {
                'server': 'RUSSIA',
                'lvl': 11,
                'champions': 11,
                'skins': 11,
                'rang': 'IRON',
                'short_description': 'test',
                'description': 'test',
                'price': 1000,
                'setting': '',
                'images': [image_file1, image_file2],
            },
            follow=True,
        )
        account.refresh_from_db()
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        account.refresh_from_db()
        self.assertFalse(account.is_archive)
        self.assertIn('RUSSIA', response.content.decode())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(account.images.count(), 2)
        self.assertIn('avatar', account.images.first().image.name)
        self.assertIn('diamond_bundle', account.images.last().image.name)
        self.client.logout()
        response = self.client.get(path)
        self.assertNotIn('Редактировать', response.content.decode())
        self.assertNotIn('Удалить аккаунт', response.content.decode())
        self.client.login(username=self.user1_username, password=self.user1_password)
        response = self.client.post(path, {'delete_account': ''}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        account.refresh_from_db()
        self.assertTrue(account.is_archive)

        path = reverse('store:store_accounts')
        response = self.client.post(
            path,
            {
                'user': self.user1,
                'server': 'EU WEST',
                'lvl': 12,
                'champions': 12,
                'skins': 12,
                'rang': 'IRON',
                'short_description': 'test1',
                'description': 'test1',
                'price': 10,
            },
            follow=True,
        )

        self.client.logout()
        self.client.login(username=self.user2_username, password=self.user2_password)
        account = AccountObject.objects.last()
        AccountOrder.objects.create(user=self.user2, account=account)
        print('23', AccountObject.objects.all().count(), AccountOrder.objects.all().count(), account)
        path = reverse('store:store_account_page', kwargs={'id': account.id})
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Оставить отзыв',response.content.decode())
        reviews_seller = ReviewSellerModel.objects.all()
        self.assertEqual(reviews_seller.count(), 0)
        response = self.client.post(path, {
            'reviewsbt' : '',
            'stars':'5',
            'reviews':'test_review_seller',
        }, follow=True)
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(reviews_seller.count(), 1)
        self.assertIn('test_review_seller',response.content.decode())



class WebSocketTest(ChannelsLiveServerTestCase):
    async def connect_and_authenticate(self, communicator):
        # Соединяемся с WebSocket
        connected, subprotocol = await communicator.connect()
        if not connected:
            print(f'LALALA: {communicator}')
        return connected, subprotocol

    async def test_message_exchange(self):
        user1 = await self.create_user(username='user1', password='password1')
        user2 = await self.create_user(username='user2', password='password2')
        await self.add_balance(user1, 1000)
        base_balance_user1 = user1.balance
        base_balance_user2 = user2.balance
        print('User balance', user1.balance)
        account = await self.create_account(user2)
        chatroom = await self.create_chatroom(user1, user2, account)

        print(f'Chatroom ID: {chatroom.id}', user1.id, user2.id, chatroom.seller_id)
        print(f'WebSocket URL: /ws/chat/{chatroom.id}/')

        communicator_user1 = WebsocketCommunicator(ChatConsumer.as_asgi(), f'ws/chat/{chatroom.pk}/')
        communicator_user2 = WebsocketCommunicator(ChatConsumer.as_asgi(), f'ws/chat/{chatroom.pk}/')
        communicator_user1.scope['url_route'] = {'kwargs': {'room_id': chatroom.id}}
        communicator_user1.scope['user'] = user1
        communicator_user2.scope['url_route'] = {'kwargs': {'room_id': chatroom.id}}
        communicator_user2.scope['user'] = user2

        connected_user1, _ = await self.connect_and_authenticate(communicator_user1)
        connected_user2, _ = await self.connect_and_authenticate(communicator_user2)
        self.assertTrue(connected_user1)
        self.assertTrue(connected_user2)

        # Отправляем сообщение от пользователя 1
        message_from_user1 = 'Привет, пользователь 2!'
        await communicator_user1.send_json_to({'type': 'chat_message', 'message': message_from_user1})

        # Проверяем, что пользователь 1 получил своё сообщение
        response_user1 = await communicator_user1.receive_json_from()
        self.assertEqual(response_user1['type'], 'chat_message')
        self.assertEqual(response_user1['message'], message_from_user1)

        # Проверяем, что пользователь 2 получил сообщение
        response_user2 = await communicator_user2.receive_json_from()
        self.assertEqual(response_user2['type'], 'chat_message')
        self.assertEqual(response_user2['message'], message_from_user1)

        # Отправляем сообщение от пользователя 2
        message_from_user2 = 'Привет, пользователь 1!'
        await communicator_user2.send_json_to({'type': 'chat_message', 'message': message_from_user2})

        # Проверяем, что пользователь 2 получил своё сообщение
        response_user2 = await communicator_user2.receive_json_from()
        self.assertEqual(response_user2['type'], 'chat_message')
        self.assertEqual(response_user2['message'], message_from_user2)

        # Проверяем, что пользователь 1 получил сообщение от пользователя 2
        response_user1 = await communicator_user1.receive_json_from()
        self.assertEqual(response_user1['type'], 'chat_message')
        self.assertEqual(response_user1['message'], message_from_user2)

        self.assertTrue(account.is_active)

        # Покупка
        await communicator_user1.send_json_to({'type': 'buy_account'})
        response_user2 = await communicator_user2.receive_json_from()
        response_user1 = await communicator_user1.receive_json_from()
        self.assertEqual(response_user2['type'], 'buy_account')

        is_active = await self.get_account_status(account.id)
        balance = await self.get_user_balance(user1.id)

        print(f'Account is active: {is_active}, User balance: {balance}')

        self.assertFalse(is_active)
        self.assertEqual(balance, base_balance_user1 - account.price)

        print('ler', account.user.username)
        # Отмена покупки
        await communicator_user2.send_json_to({'type': 'buy_account_cancel'})
        response_user1 = await communicator_user1.receive_json_from()
        response_user2 = await communicator_user2.receive_json_from()

        self.assertEqual(response_user1['type'], 'buy_account_cancel')

        is_active = await self.get_account_status(account.id)
        balance = await self.get_user_balance(user1.id)

        self.assertTrue(is_active)
        self.assertEqual(balance, base_balance_user1)

        # Подтверждение покупки
        await communicator_user1.send_json_to({'type': 'buy_account'})
        response_user2 = await communicator_user2.receive_json_from()
        response_user1 = await communicator_user1.receive_json_from()
        self.assertEqual(response_user2['type'], 'buy_account')

        is_active = await self.get_account_status(account.id)
        balance = await self.get_user_balance(user1.id)

        self.assertFalse(is_active)
        self.assertEqual(balance, base_balance_user1 - account.price)

        await communicator_user1.send_json_to({'type': 'buy_account_acept'})
        response_user2 = await communicator_user2.receive_json_from()
        response_user1 = await communicator_user1.receive_json_from()

        is_active = await self.get_account_status(account.id)
        balance = await self.get_user_balance(user2.id)

        await self.refresh_user_and_account(user2, account)
        self.assertFalse(is_active)
        self.assertEqual(balance, base_balance_user2 + account.price)
        self.assertTrue(account.is_confirmed)

        # Закрываем соединения
        await communicator_user1.disconnect()
        await communicator_user2.disconnect()

    @database_sync_to_async
    def refresh_user_and_account(self, user, account):
        user.refresh_from_db()
        account.refresh_from_db()

    @database_sync_to_async
    def add_balance(self, user, amount):
        user.balance += amount
        user.save()
        return user

    @database_sync_to_async
    def create_user(self, username, password):
        return get_user_model().objects.create_user(username=username, password=password)

    @database_sync_to_async
    def create_account(self, user):
        return AccountObject.objects.create(
            user=user,
            server='EU WEST',
            lvl=11,
            champions=11,
            skins=11,
            rang='IRON',
            short_description='test',
            description='test',
            price=100,
            is_active=True,
        )

    @database_sync_to_async
    def create_chatroom(self, buyer, seller, account):
        return ChatRoom.objects.create(buyer=buyer, seller=seller, account=account)

    @database_sync_to_async
    def get_account_status(self, account_id):
        return AccountObject.objects.get(id=account_id).is_active

    @database_sync_to_async
    def get_user_balance(self, user_id):
        return get_user_model().objects.get(id=user_id).balance


class NotificationWebSocketTest(ChannelsLiveServerTestCase):
    async def connect_and_authenticate(self, communicator):
        # Соединяемся с WebSocket
        connected, subprotocol = await communicator.connect()
        if not connected:
            print(f'LALALA: {communicator}')
        return connected, subprotocol

    async def test_message_exchange(self):
        user1 = await self.create_user(username='user1', password='password1')
        user2 = await self.create_user(username='user2', password='password2')

        account = await self.create_account(user2)
        chatroom = await self.create_chatroom(user1, user2, account)

        print(f'Chatroom ID: {chatroom.id}', user1.id, user2.id, chatroom.seller_id)
        print(f'WebSocket URL: /ws/chat/{chatroom.id}/')

        communicator_user1 = WebsocketCommunicator(ChatConsumer.as_asgi(), f'ws/chat/{chatroom.pk}/')
        communicator_user2 = WebsocketCommunicator(ChatConsumer.as_asgi(), f'ws/chat/{chatroom.pk}/')
        communicator_user1.scope['url_route'] = {'kwargs': {'room_id': chatroom.id}}
        communicator_user1.scope['user'] = user1
        communicator_user2.scope['url_route'] = {'kwargs': {'room_id': chatroom.id}}
        communicator_user2.scope['user'] = user2

        connected_user1, _ = await self.connect_and_authenticate(communicator_user1)
        connected_user2, _ = await self.connect_and_authenticate(communicator_user2)
        self.assertTrue(connected_user1)
        self.assertTrue(connected_user2)

        communicator_notification_user1 = WebsocketCommunicator(
            NotificationConsumer.as_asgi(), 'ws/notification/'
        )
        communicator_notification_user2 = WebsocketCommunicator(
            NotificationConsumer.as_asgi(), 'ws/notification/'
        )
        communicator_notification_user1.scope['user'] = user1
        communicator_notification_user2.scope['user'] = user2

        connected_notification_user1, _ = await self.connect_and_authenticate(
            communicator_notification_user1
        )
        connected_notification_user2, _ = await self.connect_and_authenticate(
            communicator_notification_user2
        )
        print('142', connected_notification_user1)
        self.assertTrue(connected_notification_user1)
        self.assertTrue(connected_notification_user2)

        # Отправляем сообщение от пользователя 1
        message_from_user1 = 'Привет, пользователь 2!'
        await communicator_user1.send_json_to({'type': 'chat_message', 'message': message_from_user1})

        # Проверяем, что пользователь 1 получил своё сообщение
        response_user1 = await communicator_user1.receive_json_from()
        self.assertEqual(response_user1['type'], 'chat_message')
        self.assertEqual(response_user1['message'], message_from_user1)

        # Проверяем, что пользователь 2 получил сообщение notification
        response_user2 = await communicator_notification_user2.receive_json_from()
        self.assertEqual(response_user2['type'], 'notification')
        self.assertEqual(response_user2['message_content'], message_from_user1)

        # Проверяем, что пользователь 2 получил своё сообщение
        response_user2 = await communicator_user2.receive_json_from()
        self.assertEqual(response_user2['type'], 'chat_message')
        self.assertEqual(response_user2['message'], message_from_user1)

        # Отправляем сообщение от пользователя 2
        message_from_user2 = 'Привет, пользователь 1!'
        await communicator_user2.send_json_to({'type': 'chat_message', 'message': message_from_user2})

        # Проверяем, что пользователь 2 получил своё сообщение
        response_user2 = await communicator_user2.receive_json_from()
        self.assertEqual(response_user2['type'], 'chat_message')
        self.assertEqual(response_user2['message'], message_from_user2)

        # Проверяем, что пользователь 1 получил сообщение
        response_user1 = await communicator_notification_user1.receive_json_from()
        self.assertEqual(response_user1['type'], 'notification')
        self.assertEqual(response_user1['message_content'], message_from_user2)

    @database_sync_to_async
    def create_user(self, username, password):
        return get_user_model().objects.create_user(username=username, password=password)

    @database_sync_to_async
    def create_account(self, user):
        return AccountObject.objects.create(
            user=user,
            server='EU WEST',
            lvl=11,
            champions=11,
            skins=11,
            rang='IRON',
            short_description='test',
            description='test',
            price=100,
            is_active=True,
        )

    @database_sync_to_async
    def create_chatroom(self, buyer, seller, account):
        return ChatRoom.objects.create(buyer=buyer, seller=seller, account=account)

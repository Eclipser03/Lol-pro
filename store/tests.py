import json
import os
from http import HTTPStatus

from django.utils.timezone import make_aware
from datetime import datetime
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from store.models import Coupon
from store.services import calculate_boost, calculate_qualification
from user.models import User


# Create your tests here.


class StoreTestCase(TestCase):
    @classmethod
    def setUp(cls):
        cls.user1_username = cls.user1_password = 'user1'
        cls.user1_email = 'user1@yandex.ru'

        cls.user1 = User.objects.create_user(cls.user1_username, cls.user1_email, cls.user1_password)
        cls.user1.balance = 100000
        cls.user1.save()

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
        self.assertEqual(self.user1.balance, 100000- price)
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
            path, data, follow=True,
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
            path, data, follow=True,
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
            path, data, follow=True,
        )
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.balance, 100000 - calculate_qualification(data))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.user1.qualification_orders.all().count(), 1)

    def test_placement_matches_purchase_coupon(self):
        coupon = Coupon.objects.create(name='test', sale=20, is_active=True, end_date='2025-10-10', count=200)
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
            'coupon_code': 'test'
        }
        self.client.login(username=self.user1_username, password=self.user1_password)
        path = reverse('store:placement_matches')
        self.assertEqual(self.user1.balance, 100000)
        self.assertEqual(self.user1.qualification_orders.all().count(), 0)
        response = self.client.post(
            path, data, follow=True,
        )
        data['coupon_code'] = coupon
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.balance, 100000 - calculate_qualification(data))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.user1.qualification_orders.all().count(), 1)
        coupon.refresh_from_db()
        data['coupon_code'] = 'test'
        response = self.client.post(
            path, data, follow=True,
        )
        print(response.content.decode())
        print(self.user1.qualification_orders.last().coupon_code)
        self.assertEqual(self.user1.qualification_orders.all().count(), 1)

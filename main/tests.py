from urllib import response
from django.test import TestCase
from django.urls import reverse

from user.models import User

# Create your tests here.


class MainViewTestCase(TestCase):

    @classmethod
    def setUp(cls):
        cls.path = reverse('main:home')
        cls.user1_username = cls.user1_password = "user1"
        cls.user1_email = "user1@yandex.ru"

        cls.user1 = User.objects.create_user(cls.user1_username, cls.user1_email, cls.user1_password)

    def test_home_page_status(self):
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/index.html')

    def test_home_page_title_btn(self):
        response = self.client.get(self.path)
        self.assertEqual(response.context_data['title'], 'Главная')
        self.assertIn('Войти', response.content.decode())

    def test_home_page_login(self):
        self.assertTrue(self.client.login(username=self.user1_username, password=self.user1_password))
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Войти', response.content.decode())
        self.assertIn(self.user1_username, response.content.decode())
        self.assertIn('Баланс', response.content.decode())

from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus
from user.models import User

# Create your tests here.


class UserTestCase(TestCase):
    @classmethod
    def setUp(cls):
        cls.user1_username = cls.user1_password = "user1"
        cls.user1_email = "user1@yandex.ru"
        cls.registration_data = {
            'username': 'user12',
            'password1': 'wor12345',
            'password2': 'wor12345',
            'email': 'eclipser@yandex.ru',
            'checkbox': True,
            'captcha': 'PASSED',
        }
        cls.user1 = User.objects.create_user(cls.user1_username, cls.user1_email, cls.user1_password)

    def test_registration_page_status(self):
        path = reverse('user:registration')
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)

    @patch("django_recaptcha.fields.ReCaptchaField.validate")
    def test_registration_form(self, validate_method):
        path = reverse('user:registration')
        response = self.client.post(path, self.registration_data)
        print(response.content.decode())
        validate_method.return_value = True
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('main:home'))
        self.assertTrue(User.objects.filter(username=self.registration_data['username']).exists())
        self.assertTrue(User.objects.get(username=self.registration_data['username']).is_active)

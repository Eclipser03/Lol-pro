from http import HTTPStatus
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from user.models import User


# Create your tests here.


class UserTestCase(TestCase):
    @classmethod
    def setUp(cls):
        cls.user1_username = cls.user1_password = 'user1'
        cls.user1_email = 'user1@yandex.ru'

        cls.user1 = User.objects.create_user(cls.user1_username, cls.user1_email, cls.user1_password)

    def test_registration_page_status(self):
        path = reverse('user:registration')
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)

    @patch('django_recaptcha.fields.ReCaptchaField.validate')
    def test_registration_form(self, validate_method):
        data = {
            'username': 'user12',
            'password1': 'wor12345',
            'password2': 'wor12345',
            'email': 'eclipser@yandex.ru',
            'checkbox': True,
            'captcha': 'PASSED',
        }
        path = reverse('user:registration')
        response = self.client.post(path, data)
        validate_method.return_value = True
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('main:home'))
        self.assertTrue(User.objects.filter(username=data['username']).exists())
        self.assertTrue(User.objects.get(username=data['username']).is_active)

    @patch('django_recaptcha.fields.ReCaptchaField.validate')
    def test_registration_form_login_error(self, validate_method):
        data = {
            'username': 'user12',
            'password1': 'wor12345',
            'password2': 'wor12345',
            'email': 'eclipser@yandex.ru',
            'checkbox': True,
            'captcha': 'PASSED',
        }
        data_login = {
            'username': 'user12',
            'password1': 'wor12345',
            'password2': 'wor12345',
            'email': 'eclipser1@yandex.ru',
            'checkbox': True,
            'captcha': 'PASSED',
        }
        validate_method.return_value = True
        path = reverse('user:registration')

        self.assertFalse(User.objects.filter(username='user12').exists())
        response = self.client.post(path, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(User.objects.filter(username='user12').exists())
        self.client.logout()

        response = self.client.post(path, data_login)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Пользователь с таким именем уже существует.', response.content.decode())

    @patch('django_recaptcha.fields.ReCaptchaField.validate')
    def test_registration_form_password_error(self, validate_method):
        data = {
            'username': 'user12',
            'password1': 'wor12345',
            'password2': 'wor12345',
            'email': 'eclipser@yandex.ru',
            'checkbox': True,
            'captcha': 'PASSED',
        }
        data_pass = {
            'username': 'user123',
            'password1': 'wor1234',
            'password2': 'wor12345',
            'email': 'eclipser1@yandex.ru',
            'checkbox': True,
            'captcha': 'PASSED',
        }
        data_pass_1 = {
            'username': 'user123',
            'password1': 'wor',
            'password2': 'wor',
            'email': 'eclipser1@yandex.ru',
            'checkbox': True,
            'captcha': 'PASSED',
        }
        validate_method.return_value = True
        path = reverse('user:registration')

        self.assertFalse(User.objects.filter(username='user12').exists())
        response = self.client.post(path, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(User.objects.filter(username='user12').exists())
        self.client.logout()

        response = self.client.post(path, data_pass)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Введенные пароли не совпадают.', response.content.decode())


        response = self.client.post(path, data_pass_1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Введённый пароль слишком короткий. Он должен содержать как минимум 8 символов.', response.content.decode())


    @patch('django_recaptcha.fields.ReCaptchaField.validate')
    def test_registration_form_email_error(self, validate_method):
        data = {
            'username': 'user12',
            'password1': 'wor12345',
            'password2': 'wor12345',
            'email': 'eclipser@yandex.ru',
            'checkbox': True,
            'captcha': 'PASSED',
        }
        data_email = {
            'username': 'user123',
            'password1': 'wor12345',
            'password2': 'wor12345',
            'email': 'eclipser1@yandex.',
            'checkbox': True,
            'captcha': 'PASSED',
        }
        data_email_1 = {
            'username': 'user123',
            'password1': 'wor12345',
            'password2': 'wor12345',
            'email': 'eclipser1yandex.ru',
            'checkbox': True,
            'captcha': 'PASSED',
        }
        validate_method.return_value = True
        path = reverse('user:registration')

        self.assertFalse(User.objects.filter(username='user12').exists())
        response = self.client.post(path, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(User.objects.filter(username='user12').exists())
        self.client.logout()

        response = self.client.post(path, data_email)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Введите правильный адрес электронной почты.', response.content.decode())


        response = self.client.post(path, data_email_1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Введите правильный адрес электронной почты.', response.content.decode())


    @patch('django_recaptcha.fields.ReCaptchaField.validate')
    def test_registration_form_chekbox_error(self, validate_method):
        data = {
            'username': 'user12',
            'password1': 'wor12345',
            'password2': 'wor12345',
            'email': 'eclipser@yandex.ru',
            'checkbox': True,
            'captcha': 'PASSED',
        }
        data_chekbox = {
            'username': 'user123',
            'password1': 'wor12345',
            'password2': 'wor12345',
            'email': 'eclipser1@yandex.ru',
            'checkbox': False,
            'captcha': 'PASSED',
        }
        validate_method.return_value = True
        path = reverse('user:registration')

        self.assertFalse(User.objects.filter(username='user12').exists())
        response = self.client.post(path, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(User.objects.filter(username='user12').exists())
        self.client.logout()

        response = self.client.post(path, data_chekbox)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Обязательное поле.', response.content.decode())

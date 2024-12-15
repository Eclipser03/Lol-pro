from http import HTTPStatus
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from store.models import BoostOrder, RPorder
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
        self.assertIn(
            'Введённый пароль слишком короткий. Он должен содержать как минимум 8 символов.',
            response.content.decode(),
        )

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

    def test_login_page_status(self):
        path = reverse('user:login')
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)

    def test_login_form(self):
        path = reverse('user:login')
        response = self.client.post(
            path, {'username': self.user1_username, 'password': self.user1_password}
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_login_form_error(self):
        path = reverse('user:login')
        response = self.client.post(path, {'username': self.user1_username, 'password': '12345'})
        self.assertIn(
            'Пожалуйста, введите правильные имя пользователя и пароль. Оба поля могут быть чувствительны к регистру.',
            response.content.decode(),
        )

    def test_login_form_chekbox_true(self):
        path = reverse('user:login')
        response = self.client.post(
            path, {'username': self.user1_username, 'password': self.user1_password, 'checkbox': True}
        )
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        session_age = self.client.session.get_expiry_age()
        self.assertEqual(session_age, 60 * 60 * 24 * 30)

    def test_login_form_chekbox_false(self):
        path = reverse('user:login')
        response = self.client.post(
            path, {'username': self.user1_username, 'password': self.user1_password, 'checkbox': False}
        )
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        session_age = self.client.session.get_expiry_age()
        self.assertEqual(session_age, 0)


class ProfileTestCase(TestCase):
    def setUp(self):
        # self.user_username = self.user_password = 'user1'
        # self.user_email = 'user1@yandex.ru'
        # User.objects.create_user(username=self.user_username, password=self.user_password, email=self.user_email)
        # self.client.login(username=self.user_username,password=self.user_password)
        self.user = User.objects.create_user(
            username='testuser', password='password123', email='test@yandex.ru'
        )
        self.client.login(username='testuser', password='password123')

    def test_profile_status(self):
        path = reverse('user:profile')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Изменить пароль', response.content.decode())
        self.assertIn('Изменить почту', response.content.decode())
        self.assertIn('Пополнить баланс', response.content.decode())

    def test_profile_avatar(self):
        path = reverse('user:profile')
        avatar = SimpleUploadedFile(
            name='test_avatar.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x02\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x02\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b',
            content_type='image/jpeg',
        )
        response = self.client.post(
            path,
            {
                'avatar': avatar,
                'update_profile': '',
            },
            follow=True,
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIn('test_avatar', self.user.avatar.name)

    def test_profile_game_username(self):
        path = reverse('user:profile')
        response = self.client.post(
            path,
            {
                'game_username': 'eclipser',
                'update_profile': '',
            },
            follow=True,
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIn('eclipser', self.user.game_username)

    def test_profile_game_username_error(self):
        path = reverse('user:profile')
        response = self.client.post(
            path,
            {
                'game_username': 'eclipsereclipsereclipsereclipsereclipsereclipsereclipsereclipsereclipsereclipser',
                'update_profile': '',
            },
            follow=True,
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'Убедитесь, что это значение содержит не более 30 символов', response.content.decode()
        )

    def test_profile_discord(self):
        path = reverse('user:profile')
        response = self.client.post(
            path,
            {
                'discord': 'eclipser',
                'update_profile': '',
            },
            follow=True,
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIn('eclipser', self.user.discord)

    def test_profile_discorde_error(self):
        path = reverse('user:profile')
        response = self.client.post(
            path,
            {
                'discord': 'eclipsereclipsereclipsereclipsereclipsereclipsereclipsereclipsereclipsereclipser',
                'update_profile': '',
            },
            follow=True,
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'Убедитесь, что это значение содержит не более 30 символов', response.content.decode()
        )

    def test_profile_balance(self):
        path = reverse('user:profile')
        response = self.client.post(path, {'update_balance': '', 'balance': 100}, follow=True)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.balance, 100)

    def test_profile_balance_error(self):
        path = reverse('user:profile')
        response = self.client.post(path, {'update_balance': '', 'balance': -100}, follow=True)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Введите положительную сумму', response.content.decode())

    def test_profile_email(self):
        path = reverse('user:profile')
        response = self.client.post(
            path, {'update_email': '', 'new_email': 'eclipser@yandex.ru'}, follow=True
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Письмо отправлено на Вашу почту!', response.content.decode())

    def test_profile_email_error(self):
        path = reverse('user:profile')
        response = self.client.post(path, {'update_email': '', 'new_email': 'eclipser'}, follow=True)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        print(response.content.decode())
        self.assertIn('Введите правильный адрес электронной почты.', response.content.decode())

    def test_profile_email_error1(self):
        path = reverse('user:profile')
        response = self.client.post(
            path, {'update_email': '', 'new_email': 'test@yandex.ru'}, follow=True
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Этот email уже используется.', response.content.decode())

    def test_profile_password(self):
        path = reverse('user:profile')
        new_password = 'wor12345'
        response = self.client.post(
            path,
            {
                'update_password': '',
                'old_password': 'password123',
                'new_password1': new_password,
                'new_password2': new_password,
            },
            follow=True,
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        print(response.content.decode())
        self.assertIn('Пароль успешно изменен', response.content.decode())
        self.assertTrue(self.user.check_password(new_password))

    def test_profile_password_error(self):
        path = reverse('user:profile')
        response = self.client.post(
            path,
            {
                'update_password': '',
                'old_password': 'password123',
                'new_password1': 'wor12345',
                'new_password2': 'wor123456',
            },
            follow=True,
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Введенные пароли не совпадают.', response.content.decode())

    def test_profile_password_error1(self):
        path = reverse('user:profile')
        response = self.client.post(
            path,
            {
                'update_password': '',
                'old_password': 'password123',
                'new_password1': 'wor123',
                'new_password2': 'wor123',
            },
            follow=True,
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'Введённый пароль слишком короткий. Он должен содержать как минимум 8 символов.',
            response.content.decode(),
        )

    def test_profile_password_error2(self):
        path = reverse('user:profile')
        response = self.client.post(
            path,
            {
                'update_password': '',
                'old_password': 'password',
                'new_password1': 'wor12345',
                'new_password2': 'wor12345',
            },
            follow=True,
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Неправильно введен текущий пароль', response.content.decode())

    def test_profile_products(self):
        path = reverse('user:profile')
        response = self.client.get(path)
        self.assertNotIn('Заказ Риот Поинтов от testuser', response.content.decode())
        RPorder.objects.create(
            user=self.user, rp=1000, price_rub=230, server='EU WEST', account_name='eclipser'
        )
        response = self.client.get(path)
        self.assertIn('Заказ Риот Поинтов от testuser', response.content.decode())

    def test_profile_boost(self):
        path = reverse('user:profile')
        response = self.client.get(path)
        self.assertNotIn('Буст', response.content.decode())
        BoostOrder.objects.create(
            user=self.user,
            current_position='1',
            current_division='2',
            current_lp='1',
            desired_position='3',
            desired_division='2',
            lp_per_win='1',
            server='1',
            queue_type='1',
            specific_role=False,
            duo_booster=False,
            total_time='1',
            total_price='1',
        )
        response = self.client.get(path)
        self.assertIn('Буст', response.content.decode())

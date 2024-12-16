from http import HTTPStatus
from urllib import response
from django.test import TestCase
from django.urls import reverse
from django.utils.formats import number_format

from main.models import ReviewModel
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

class ReviewsTestCase(TestCase):
    @classmethod
    def setUp(cls):
        cls.user1_username = cls.user1_password = "user1"
        cls.user1_email = "user1@yandex.ru"

        cls.user1 = User.objects.create_user(cls.user1_username, cls.user1_email, cls.user1_password)

    def test_reviews_page(self):
        path = reverse('main:reviews')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Отзывы о сайте', response.content.decode())
        self.assertIn('Пока что нет отзывов', response.content.decode())

    def test_reviews_calculate(self):
        path = reverse('main:reviews')
        response = self.client.get(path)
        self.assertIn('Пока что нет отзывов', response.content.decode())
        ReviewModel.objects.create(user=self.user1, stars=5, reviews='test')
        ReviewModel.objects.create(user=self.user1, stars=3, reviews='test')
        ReviewModel.objects.create(user=self.user1, stars=3, reviews='test')
        reviews = ReviewModel.objects.all()
        stars_list = list(map(int, reviews.values_list('stars', flat=True)))
        average_stars = round(sum(stars_list) / len(stars_list), 1)
        formatted_average = number_format(average_stars, decimal_pos=1)
        response = self.client.get(path)
        self.assertIn(f'Средний рейтинг: {formatted_average}', response.content.decode())

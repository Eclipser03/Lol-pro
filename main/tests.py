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

    def test_reviews_post(self):
        path = reverse('main:reviews')
        response = self.client.post(path, {'stars':'5', 'reviews': 'test_review', 'user':self.user1}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Вход в личный кабинет', response.content.decode())
        self.client.login(username=self.user1_username, password=self.user1_password)
        path = reverse('main:reviews')
        response = self.client.post(path, {'stars':'5', 'reviews': 'test_review', 'user':self.user1}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Отзывы о сайте', response.content.decode())
        self.assertIn('test_review', response.content.decode())
        path = reverse('main:reviews')
        response = self.client.post(path, {
            'stars':'5',
            'reviews': 'ALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALADASD',
            'user':self.user1
            }, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Отзывы о сайте', response.content.decode())
        self.assertIn('Убедитесь, что это значение содержит не более 300 символов', response.content.decode())

    def test_reviews_calculate(self):
        path = reverse('main:reviews')
        response = self.client.get(path)
        self.assertIn('Пока что нет отзывов', response.content.decode())
        ReviewModel.objects.create(user=self.user1, stars=5, reviews='test1')
        ReviewModel.objects.create(user=self.user1, stars=3, reviews='test2')
        ReviewModel.objects.create(user=self.user1, stars=3, reviews='test3')
        reviews = ReviewModel.objects.all()
        self.assertEqual(reviews.count(), 3)
        stars_list = list(map(int, reviews.values_list('stars', flat=True)))
        average_stars = round(sum(stars_list) / len(stars_list), 1)
        formatted_average = number_format(average_stars, decimal_pos=1)
        response = self.client.get(path)
        self.assertIn(f'Средний рейтинг: {formatted_average}', response.content.decode())
        self.assertIn('test1', response.content.decode())
        self.assertIn('test2', response.content.decode())
        self.assertIn('test3', response.content.decode())
        review_last = ReviewModel.objects.last()
        ReviewModel.objects.create(user=self.user1, parent=review_last, reviews='test4')
        reviews = ReviewModel.objects.all()
        self.assertEqual(reviews.count(), 4)
        self.assertEqual(review_last.children.count(), 1)
        response = self.client.get(path)
        self.assertIn('test4', response.content.decode())

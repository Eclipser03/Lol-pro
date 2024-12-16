from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from news.models import News


# Create your tests here.


class NewsTestCase(TestCase):
    def test_news_page(self):
        path = reverse('news:news')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Новости', response.content.decode())

    def test_news_one(self):
        path = reverse('news:news')
        response = self.client.get(path)
        self.assertNotIn('testtitle', response.content.decode())
        News.objects.create(
            title='testtitle', description='test', url='test', date_published='2024-10-11'
        )
        response = self.client.get(path)
        self.assertIn('testtitle', response.content.decode())

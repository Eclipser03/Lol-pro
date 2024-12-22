from django.core.management.base import BaseCommand

from news.services import parse_news


class Command(BaseCommand):
    help = 'Парсинг новостей'

    def handle(self, *args, **options):
        parse_news()

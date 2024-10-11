from celery import shared_task

from news.services import parse_news


@shared_task
def parse_news_task():
    parse_news()

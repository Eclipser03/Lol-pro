from celery.schedules import crontab

from lol_pay.settings.base import TIME_ZONE
from lol_pay.settings.cache import REDIS_HOST, REDIS_PORT


CELERY_BROKER_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

CELERY_BEAT_SCHEDULE = {
    'parse-news-every-day': {
        'task': 'news.tasks.parse_news_task',
        'schedule': crontab(hour=0, minute=0),
    },
}

CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

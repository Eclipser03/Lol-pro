import os
from os import getenv

from lol_pay.settings.base import BASE_DIR


REDIS_HOST = getenv('REDIS_HOST') if not os.environ.get('RUN_FROM_DOCKER') else 'redis'
REDIS_PORT = getenv('REDIS_PORT')
print(REDIS_HOST)

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(REDIS_HOST, REDIS_PORT)],
        },
    },
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': (BASE_DIR / 'cache'),
    }
}


SESSION_COOKIE_AGE = 60 * 60 * 24 * 7 * 2

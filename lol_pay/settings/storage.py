import os
from os import getenv

from lol_pay.settings.base import BASE_DIR, DEBUG


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': getenv('POSTGRES_DB'),
        'USER': getenv('POSTGRES_USER'),
        'PASSWORD': getenv('POSTGRES_PASSWORD'),
        'HOST': getenv('POSTGRES_HOST') if not bool(os.environ.get('RUN_FROM_DOCKER')) else 'postgres',
        'PORT': getenv('POSTGRES_PORT'),
    }
}

STATIC_URL = '/static/'

if DEBUG:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

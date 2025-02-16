from os import getenv
from pathlib import Path

from django.conf.global_settings import DEFAULT_FROM_EMAIL, SERVER_EMAIL
from dotenv import find_dotenv, load_dotenv


DEBUG = True

ALLOWED_HOSTS = ['*']

load_dotenv(find_dotenv())

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = getenv('SECRET_KEY')

if not SECRET_KEY:
    raise ValueError('SECRET_KEY не задан в .env')


INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_recaptcha',
    'debug_toolbar',
    'tinymce',
    'mptt',
    'channels',
    'channels_redis',
    'django_filters',
    'user',
    'main',
    'news',
    'store',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'user.middleware.ActiveUserMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'lol_pay.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ASGI_APPLICATION = 'lol_pay.asgi.application'
WSGI_APPLICATION = 'lol_pay.wsgi.application'


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


RECAPTCHA_PUBLIC_KEY = getenv('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = getenv('RECAPTCHA_PRIVATE_KEY')

# user

AUTH_USER_MODEL = 'user.User'
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'

# mail

EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = '465'
EMAIL_HOST_USER = getenv('EMAIL_HOST_USER')
EMAIL_USE_SSL = True
EMAIL_HOST_PASSWORD = getenv('EMAIL_HOST_PASSWORD')


DEFAULT_FROM_EMAIL = EMAIL_HOST_USER  # noqa: F811
SERVER_EMAIL = EMAIL_HOST_USER  # noqa: F811
EMAIL_ADMIN = EMAIL_HOST_USER


# Tinymce

TINYMCE_DEFAULT_CONFIG = {
    'height': 320,
    'width': 960,
    'plugins': 'link image preview codesample table code lists fullscreen',
    'toolbar': 'undo redo | bold italic | alignleft aligncenter alignright |\
        bullist numlist | link image | preview code fullscreen',
}

INTERNAL_IPS = [
    '127.0.0.1',
]

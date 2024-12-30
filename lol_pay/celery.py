import os

from celery import Celery


# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lol_pay.settings')

# Создаем экземпляр Celery
app = Celery('lol_pay')

# Загружаем конфигурацию из Django настроек, используя пространство имен 'CELERY'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи (tasks.py) в приложениях проекта
app.autodiscover_tasks()

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.cache import cache
from django.utils import timezone
from django.core.cache import cache


# Create your models here.
class User(AbstractUser):
    avatar = models.ImageField(upload_to='users_avatar', null=True, blank=True, default='avatar.jpg')
    game_username = models.CharField(max_length=100, blank=True, null=True)
    discord = models.CharField(max_length=100, blank=True, null=True)

    def is_online(self):
        last_seen = cache.get(f'last-seen-{self.id}')
        if last_seen is not None and timezone.now() < last_seen + timezone.timedelta(seconds=300):
            return True
        return False

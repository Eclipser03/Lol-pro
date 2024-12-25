from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    avatar = models.ImageField(
        upload_to='users_avatar', null=True, blank=True, default='avatar.jpg', verbose_name='Аватар'
    )
    game_username = models.CharField(
        max_length=30, blank=True, null=True, verbose_name='Никнейм в игре', default=''
    )
    discord = models.CharField(max_length=30, blank=True, null=True, verbose_name='Дискорд')
    balance = models.IntegerField(default=0, verbose_name='Баланс', validators=[MinValueValidator(0)])

    def is_online(self):
        last_seen = cache.get(f'last-seen-{self.id}')
        return last_seen is not None and timezone.now() < last_seen + timezone.timedelta(seconds=300)

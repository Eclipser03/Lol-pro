from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    avatar = models.ImageField(upload_to='users_avatar', null=True, blank=True)
    game_username = models.CharField(max_length=100, blank=True, null=True)

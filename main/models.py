from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from user.models import User


class ReviewModel(MPTTModel):
    STARS_CHOISES = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews', verbose_name='Пользователь'
    )
    stars = models.CharField(max_length=2, choices=STARS_CHOISES, verbose_name='Оценка', blank=True)
    reviews = models.TextField(verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    parent = TreeForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children'
    )

    class MPTTMeta:
        order_insertion_by = ['created_at']

    class Meta:
        verbose_name = 'Отзыв о сайте'
        verbose_name_plural = 'Отзывы о сайте'

    def __str__(self):
        return f'Отзыв от {self.user.username}'

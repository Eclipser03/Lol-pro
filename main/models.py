from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from tinymce import models as tinymce_models

from main.choices import ReviewsStarsChoices
from user.models import User


class ReviewModel(MPTTModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews', verbose_name='Пользователь'
    )
    stars = models.IntegerField(
        choices=ReviewsStarsChoices.choices, verbose_name='Оценка', blank=True, null=True
    )
    reviews = tinymce_models.HTMLField(verbose_name='Описание', max_length=300)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    parent = TreeForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='childrens'
    )

    class MPTTMeta:
        order_insertion_by = ['-created_at']

    class Meta:
        verbose_name = 'Отзыв о сайте'
        verbose_name_plural = 'Отзывы о сайте'

    def __str__(self):
        return f'Отзыв от {self.user.username}'

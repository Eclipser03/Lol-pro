from django.db import models
from tinymce import models as tinymce_models


# Create your models here.

# Модель новостей


class News(models.Model):
    title = models.CharField(max_length=255)  # Заголовок новости
    description = tinymce_models.HTMLField()  # Описание новости
    url = models.URLField(unique=True)  # Уникальный URL для каждой новости
    date_published = models.DateField()  # Дата публикации
    image = models.URLField(blank=True, null=True)  # URL изображения, может быть пустым

    class Meta:
        verbose_name = 'новость'  # Название в единственном числе для административной панели
        verbose_name_plural = 'новости'  # Название во множественном числе для административной панели

    def __str__(self):
        return self.title  # Строковое представление модели

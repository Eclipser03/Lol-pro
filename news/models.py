from django.db import models
from tinymce import models as tinymce_models


class News(models.Model):
    title = models.CharField(max_length=255)
    description = tinymce_models.HTMLField()
    url = models.URLField(unique=True)
    date_published = models.DateField()
    image = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ('-date_published',)

    def __str__(self):
        return self.title

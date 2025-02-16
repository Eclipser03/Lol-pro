# Generated by Django 5.1.1 on 2024-11-26 12:15

import django.db.models.deletion
import mptt.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0018_message_massage_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewSellerModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stars', models.CharField(blank=True, choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], max_length=2, verbose_name='Оценка')),
                ('reviews', models.TextField(verbose_name='Отзыв')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_buyer', to=settings.AUTH_USER_MODEL, verbose_name='Покупатель')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='store.reviewsellermodel')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='store.accountobject', verbose_name='Товар')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_seller', to=settings.AUTH_USER_MODEL, verbose_name='Продавец')),
            ],
            options={
                'verbose_name': 'Отзыв о продавце',
                'verbose_name_plural': 'Отзывы о продавцах',
            },
        ),
    ]

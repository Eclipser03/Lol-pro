# Generated by Django 5.1.1 on 2024-12-30 20:35

import django.db.models.deletion
import mptt.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_alter_reviewmodel_stars'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviewmodel',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='childrens', to='main.reviewmodel'),
        ),
    ]

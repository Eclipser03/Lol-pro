# Generated by Django 5.1.1 on 2024-11-09 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_accountobject_accountorder_accountsimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountobject',
            name='short_description',
            field=models.CharField(max_length=100, verbose_name='Короткое описание'),
        ),
    ]

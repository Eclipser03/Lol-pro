# Generated by Django 5.1.1 on 2024-12-21 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0027_alter_accountobject_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='massage_type',
            field=models.CharField(blank=True, choices=[('chat_message', 'сообщение'), ('buy_account', 'бронирование аккаунта'), ('buy_account_acept', 'подтверждение покупки')], max_length=25, null=True, verbose_name='Тип сообщения'),
        ),
    ]

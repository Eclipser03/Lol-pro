# Generated by Django 5.1.1 on 2024-11-14 07:45

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_alter_message_options_chatroom_account_id'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='chatroom',
            old_name='account_id',
            new_name='account',
        ),
        migrations.AlterUniqueTogether(
            name='chatroom',
            unique_together={('buyer', 'seller', 'account')},
        ),
    ]

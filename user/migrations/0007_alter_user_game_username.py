# Generated by Django 5.1.1 on 2024-12-30 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_alter_user_game_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='game_username',
            field=models.CharField(blank=True, default='', max_length=30, verbose_name='Никнейм в игре'),
        ),
    ]

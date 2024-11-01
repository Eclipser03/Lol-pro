from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from user.models import User


# Create your models here.


class Coupon(models.Model):
    name = models.CharField(max_length=20, verbose_name='Купон')
    sale = models.IntegerField(verbose_name='Размер скидки')
    count = models.IntegerField(verbose_name='Количество купонов', default=999)
    end_date = models.DateTimeField(verbose_name='Дата окончания')
    is_active = models.BooleanField(default=False, verbose_name='Активный')

    class Meta:
        verbose_name = 'Купон'
        verbose_name_plural = 'Купоны'

    def __str__(self) -> str:
        return f'Купон {self.name}'


class BoostOrder(models.Model):
    RANK_CHOISES = [
        ('IRON', 'Железо'),
        ('BRONZE', 'Бронза'),
        ('SILVER', 'Серебро'),
        ('GOLD', 'Голд'),
        ('PLATINUM', 'Платина'),
        ('EMERALD', 'Эмеральд'),
        ('DIAMOND', 'Даймонд'),
        ('MASTER', 'Мастер'),
        ('GRANDMASTER', 'Грандмастер'),
    ]

    DIVISION_CHOISES = [
        ('DIVISION 1', 'Дивизион 1'),
        ('DIVISION 2', 'Дивизион 2'),
        ('DIVISION 3', 'Дивизион 3'),
        ('DIVISION 4', 'Дивизион 4'),
    ]

    CURRENT_LP_CHOISES = [
        ('0-20LP', '0-20LP'),
        ('21-40LP', '21-40LP'),
        ('41-60LP', '41-60LP'),
        ('61-80LP', '61-80LP'),
        ('81-99LP', '81-99LP'),
    ]

    LP_PER_WIN_CHOISES = [
        ('18+LP', '18+ LP'),
        ('15-17LP', '15-17 LP'),
        ('<15LP', '<15LP'),
    ]

    SERVER_CHOISES = [('EU WEST', 'Вест'), ('RUSSIA', 'Россия')]

    STATUS_CHOICES = [
        ('CREATED', 'Создан'),
        ('PAYED', 'Оплачен'),
        ('IN_PROCCES', 'В процессе'),
        ('CANCELED', 'Отменен'),
        ('FINISHED', 'Исполнен'),
    ]

    QUEUE_CHOICES = [
        ('SOLO/DUO', 'Соло-дуо'),
        ('FLEX', 'Флекс'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='boost_orders',
        verbose_name='Пользователь',
    )
    current_position = models.CharField(max_length=20, choices=RANK_CHOISES, verbose_name='Текущий ранг')
    current_division = models.CharField(
        max_length=20, choices=DIVISION_CHOISES, verbose_name='Текущий дивизион'
    )
    current_lp = models.CharField(max_length=20, choices=CURRENT_LP_CHOISES, verbose_name='Текущие лп')
    desired_position = models.CharField(
        max_length=20, choices=RANK_CHOISES, verbose_name='Желаемый ранг'
    )
    desired_division = models.CharField(
        max_length=20, choices=DIVISION_CHOISES, verbose_name='Желаемый дивизион'
    )
    lp_per_win = models.CharField(max_length=20, choices=LP_PER_WIN_CHOISES, verbose_name='ЛП за победу')
    server = models.CharField(max_length=20, choices=SERVER_CHOISES, verbose_name='Сервер')
    queue_type = models.CharField(max_length=20, choices=QUEUE_CHOICES, verbose_name='Режим игры')
    specific_role = models.BooleanField(verbose_name='Определенная роль')
    duo_booster = models.BooleanField(verbose_name='Игра в дуо')
    coupon_code = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='boost_orders',
        verbose_name='Купон',
    )
    total_time = models.DurationField(verbose_name='Время исполнения')
    total_price = models.IntegerField(verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Буст ордер'
        verbose_name_plural = 'Буст ордеры'

    def __str__(self):
        return f'Заказ буста от {self.user.username}: {self.current_position}\
            до {self.desired_position} на {self.server}'


class Qualification(models.Model):
    RANK_CHOISES = [
        ('IRON', 'Железо'),
        ('BRONZE', 'Бронза'),
        ('SILVER', 'Серебро'),
        ('GOLD', 'Голд'),
        ('PLATINUM', 'Платина'),
        ('EMERALD', 'Эмеральд'),
        ('DIAMOND', 'Даймонд'),
        ('MASTER', 'Мастер'),
        ('GRANDMASTER', 'Грандмастер'),
    ]

    SERVER_CHOISES = [('EU WEST', 'Вест'), ('RUSSIA', 'Россия')]

    STATUS_CHOICES = [
        ('CREATED', 'Создан'),
        ('PAYED', 'Оплачен'),
        ('IN_PROCCES', 'В процессе'),
        ('CANCELED', 'Отменен'),
        ('FINISHED', 'Исполнен'),
    ]

    QUEUE_CHOICES = [
        ('SOLO/DUO', 'Соло-дуо'),
        ('FLEX', 'Флекс'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='qualification_orders',
        verbose_name='Пользователь',
    )
    previous_position = models.CharField(
        max_length=20, choices=RANK_CHOISES, verbose_name='Ранг в прошлом сезоне'
    )
    specific_role = models.BooleanField(verbose_name='Определенная роль')
    duo_booster = models.BooleanField(verbose_name='Игра в дуо')
    game_count = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='Кол-во игр'
    )
    server = models.CharField(max_length=20, choices=SERVER_CHOISES, verbose_name='Сервер')
    queue_type = models.CharField(max_length=20, choices=QUEUE_CHOICES, verbose_name='Режим игры')
    coupon_code = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='qualification_orders',
        verbose_name='Купон',
    )
    total_time = models.DurationField(verbose_name='Время исполнения')
    total_price = models.IntegerField(verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Квалификация'
        verbose_name_plural = 'Квалификации'

    def __str__(self):
        return f'Заказ квалификации от {self.user.username}: ранг - {self.previous_position}\
            кол-во игр - {self.game_count} на {self.server}'



class SkinsOrder(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='skins_orders',
        verbose_name='Пользователь',
    )

    char_name = models.CharField(max_length=20, verbose_name='Персонаж')
    skin_name = models.CharField(max_length=20, verbose_name='Образ')
    price_char = models.IntegerField(verbose_name='Цена персонажа')
    price_skin = models.IntegerField(verbose_name='Цена образа')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Скины и персонажи'
        verbose_name_plural = 'Скины и персонажи'

    def __str__(self):
        return f'Заказ скина или персонажа от {self.user.username}'

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey

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
        return f'Буст {self.current_position} - {self.desired_position}. {self.server}'


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
        return f'Квалификация. Кол-во игр: {self.game_count}. {self.server}'


class SkinsOrder(models.Model):
    SERVER_CHOISES = [('EU WEST', 'Вест'), ('RUSSIA', 'Россия')]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='skins_orders',
        verbose_name='Пользователь',
    )

    char_name = models.CharField(max_length=50, verbose_name='Персонаж')
    skin_name = models.CharField(max_length=50, verbose_name='Образ')
    price_char = models.IntegerField(blank=True, null=True, verbose_name='Цена персонажа')
    price_skin = models.IntegerField(blank=True, null=True, verbose_name='Цена образа')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    server = server = models.CharField(
        max_length=20, choices=SERVER_CHOISES, default='EU WEST', verbose_name='Сервер'
    )
    account_name = models.CharField(
        max_length=50, verbose_name='Никнейм аккаунта', default='default_name'
    )

    class Meta:
        verbose_name = 'Скины и персонажи'
        verbose_name_plural = 'Скины и персонажи'

    def __str__(self):
        if self.char_name:
            return f'Заказ персонажа {self.char_name}'
        if self.skin_name:
            return f'Заказ образа {self.skin_name}'


class RPorder(models.Model):
    SERVER_CHOISES = [('EU WEST', 'Вест'), ('RUSSIA', 'Россия')]
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='rp_orders',
        verbose_name='Пользователь',
    )

    rp = models.IntegerField(verbose_name='Кол-во RP')
    price_rub = models.IntegerField(verbose_name='Цена')
    server = models.CharField(
        max_length=20, choices=SERVER_CHOISES, default='EU WEST', verbose_name='Сервер'
    )
    account_name = models.CharField(
        max_length=50, verbose_name='Никнейм аккаунта', default='default_name'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Риот Поинты'
        verbose_name_plural = 'Риот Поинты'

    def __str__(self):
        return f'Заказ Риот Поинтов от {self.user.username}'


class AccountObject(models.Model):
    SERVER_CHOISES = [('EU WEST', 'Вест'), ('RUSSIA', 'Россия')]

    RANK_CHOISES = [
        ('NO RANK', 'Нет ранга'),
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

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='acounts_objects',
        verbose_name='Продавец',
    )

    server = models.CharField(
        max_length=20, choices=SERVER_CHOISES, default='EU WEST', verbose_name='Сервер'
    )

    lvl = models.IntegerField(verbose_name='Уровень')
    champions = models.IntegerField(verbose_name='Количество чемпионов')
    skins = models.IntegerField(verbose_name='Количество образов')
    rang = models.CharField(max_length=20, choices=RANK_CHOISES, default='NO RANK', verbose_name='Ранг')
    short_description = models.CharField(max_length=100, verbose_name='Короткое описание')
    description = models.TextField(verbose_name='Описание', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_active = models.BooleanField(default=False, verbose_name='Проверен')
    is_confirmed = models.BooleanField(default=False, verbose_name='Покупка подтверждена')
    is_archive = models.BooleanField(default=False, verbose_name='В архиве')

    price = models.IntegerField(verbose_name='Цена')

    buyer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acounts_buyer_objects',
        verbose_name='Покупатель',
    )

    class Meta:
        verbose_name = 'Продажа аккаунта'
        verbose_name_plural = 'Продажа аккаунтов'

    def __str__(self):
        return f'Продажа аккаунта от {self.user.username}| Цена: {self.price} руб.| Id: {self.id} | Статус: {self.is_active}'

    def get_absolute_url(self):
        return reverse('store:store_account_page', kwargs={'id': self.pk})


class AccountsImage(models.Model):
    account = models.ForeignKey(AccountObject, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='acounts_images/')

    class Meta:
        verbose_name = 'Изображение для аккаунта'
        verbose_name_plural = 'Изображения для аккаунтов'

    def __str__(self):
        return f'Изображение аккаунта {self.account}'


class AccountOrder(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='acounts_orders',
        verbose_name='Покупатель',
    )

    account = models.OneToOneField(
        AccountObject,
        on_delete=models.SET_NULL,
        null=True,
        related_name='account_order',
        verbose_name='Аккаунт',
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Заказ аккаунта'
        verbose_name_plural = 'Заказы аккаунтов'

    def __str__(self):
        return f'Аккаунт для  {self.user.username}'

    def clean(self):
        if self.account and self.user == self.account.user:
            raise ValidationError('Покупатель не может быть продавцом этого аккаунта.')
        super().clean()


class ChatRoom(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_chat_rooms')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_chat_rooms')
    account = models.ForeignKey(
        AccountObject, on_delete=models.SET_NULL, null=True, blank=True, related_name='acount_chat_rooms'
    )

    class Meta:
        unique_together = ('buyer', 'seller', 'account')

    def __str__(self):
        return f'Чат между {self.buyer} и {self.seller} | номер: {self.id}'


class Message(models.Model):
    MASSAGETYPE_CHOISES = [
        ('chat_message', 'сообщение'),
        ('buy_account', 'бронирование аккаунта'),
        ('buy_account_acept', 'подтверждение покупки'),
    ]
    chat_room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    created = models.DateTimeField(default=timezone.now)
    massage_type = models.CharField(
        choices=MASSAGETYPE_CHOISES, verbose_name='Тип сообщения', blank=True, null=True
    )

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f'{self.author.username} : {self.text}'


class ReviewSellerModel(MPTTModel):
    STARS_CHOISES = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ]
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='reviews_buyer',
        verbose_name='Покупатель',
    )
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews_seller', verbose_name='Продавец'
    )
    stars = models.CharField(max_length=2, choices=STARS_CHOISES, verbose_name='Оценка', blank=True)
    reviews = models.TextField(verbose_name='Отзыв')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    parent = TreeForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children'
    )
    product = models.ForeignKey(
        AccountObject, models.CASCADE, related_name='reviews', verbose_name='Товар'
    )

    class MPTTMeta:
        order_insertion_by = ['-created_at']

    class Meta:
        verbose_name = 'Отзыв о продавце'
        verbose_name_plural = 'Отзывы о продавцах'

    def __str__(self):
        return f'Отзыв для {self.seller.username}, {self.reviews}'

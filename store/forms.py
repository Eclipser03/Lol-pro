import json
import os

from django import forms
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator

from store.models import (
    AccountObject,
    BoostOrder,
    Coupon,
    Qualification,
    ReviewSellerModel,
    RPorder,
    SkinsOrder,
)
from store.services import calculate_boost, calculate_qualification, check_coupon
from store.utils import DIVISION, LP, LP_WIN, POSITION, PRE_POSITION, QUEUE, SERVER_CHOICE


class BoostOrderForms(forms.ModelForm):
    current_position = forms.ChoiceField(
        choices=[
            ('7', 'MASTER'),
            ('6', 'DIAMOND'),
            ('5', 'EMERALD'),
            ('4', 'PLATINUM'),
            ('3', 'GOLD'),
            ('2', 'SILVER'),
            ('1', 'BRONZE'),
            ('0', 'IRON'),
        ],
        widget=forms.Select(attrs={'id': 'current-position'}),
    )
    current_division = forms.ChoiceField(
        choices=[('0', 'DIVISION 1'), ('1', 'DIVISION 2'), ('2', 'DIVISION 3'), ('3', 'DIVISION 4')],
        widget=forms.Select(attrs={'id': 'current-division'}),
    )
    current_lp = forms.ChoiceField(
        choices=[
            ('0', '0-20LP'),
            ('1', '21-40LP'),
            ('2', '41-60LP'),
            ('3', '61-80LP'),
            ('4', '81-99LP'),
        ],
        widget=forms.Select(attrs={'id': 'current-lp'}),
    )
    desired_position = forms.ChoiceField(
        choices=[
            ('8', 'GRANDMASTER'),
            ('7', 'MASTER'),
            ('6', 'DIAMOND'),
            ('5', 'EMERALD'),
            ('4', 'PLATINUM'),
            ('3', 'GOLD'),
            ('2', 'SILVER'),
            ('1', 'BRONZE'),
            ('0', 'IRON'),
        ],
        widget=forms.Select(attrs={'id': 'desired-position'}),
    )
    desired_division = forms.ChoiceField(
        choices=[('0', 'DIVISION 1'), ('1', 'DIVISION 2'), ('2', 'DIVISION 3'), ('3', 'DIVISION 4')],
        widget=forms.Select(attrs={'id': 'desired-division'}),
    )
    lp_per_win = forms.ChoiceField(
        choices=[('1', '18+LP'), ('1.1', '15-17LP'), ('1.2', '<15LP')],
        widget=forms.Select(attrs={'id': 'lp-per-win'}),
    )
    server = forms.ChoiceField(
        choices=[('1', 'EU WEST'), ('0.8', 'RUSSIA')], widget=forms.Select(attrs={'id': 'server'})
    )
    queue_type = forms.ChoiceField(
        choices=[('0', 'SOLO/DUO'), ('1', 'FLEX')], widget=forms.Select(attrs={'id': 'queue-type'})
    )
    specific_role = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={'class': 'checkbox', 'type': 'checkbox', 'id': 'specific-role', 'value': '1.2'}
        ),
        required=False,
    )
    duo_booster = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={'class': 'checkbox', 'type': 'checkbox', 'id': 'duo-booster', 'value': '1.3'}
        ),
        required=False,
    )
    coupon_code = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'coupon-code', 'placeholder': 'Ввести купон'}),
        required=False,
    )
    total_time = forms.DurationField(
        widget=forms.TextInput(attrs={'id': 'total-time-form', 'class': 'hidden'}), required=False
    )
    total_price = forms.IntegerField(
        widget=forms.TextInput(attrs={'id': 'total-price-form', 'class': 'hidden'}), required=False
    )
    user = forms.CharField(
        required=False,
    )

    class Meta:
        model = BoostOrder
        fields = {
            'current_position',
            'current_division',
            'current_lp',
            'desired_position',
            'desired_division',
            'lp_per_win',
            'server',
            'queue_type',
            'specific_role',
            'duo_booster',
            'coupon_code',
            'total_time',
            'total_price',
            'user',
        }

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['user'] = self.request.user
        coupon = cleaned_data.pop('coupon_code')

        if coupon:
            cleaned_data['coupon_code'] = Coupon.objects.get(name=coupon)

        if cleaned_data['current_position'] == cleaned_data['desired_position'] and int(
            cleaned_data['current_division']
        ) <= int(cleaned_data['desired_division']):
            raise forms.ValidationError('Текущий дивизион не может быть больше желаемого')

        if int(cleaned_data['current_position']) > int(cleaned_data['desired_position']):
            raise forms.ValidationError('Текущая позиция не может быть больше желаемой')

        if cleaned_data['total_price'] != calculate_boost(cleaned_data):
            raise forms.ValidationError('Цена не совпадает, где-то ошибка')

        if cleaned_data['total_time'].total_seconds() == 0:
            raise forms.ValidationError('Время не может быть равно 0, где-то ошибка')

        cleaned_data['current_position'] = POSITION[cleaned_data['current_position']]
        cleaned_data['current_division'] = DIVISION[cleaned_data['current_division']]
        cleaned_data['current_lp'] = LP[cleaned_data['current_lp']]
        cleaned_data['desired_position'] = POSITION[cleaned_data['desired_position']]
        cleaned_data['desired_division'] = DIVISION[cleaned_data['desired_division']]
        cleaned_data['lp_per_win'] = LP_WIN[cleaned_data['lp_per_win']]
        cleaned_data['server'] = SERVER_CHOICE[cleaned_data['server']]
        cleaned_data['queue_type'] = QUEUE[cleaned_data['queue_type']]

        if cleaned_data['user'].balance < cleaned_data['total_price']:
            raise forms.ValidationError('Пополните баланс')

        return cleaned_data

    def save(self, commit=True):
        super().save(commit=True)
        user = self.request.user
        user.balance -= self.instance.total_price
        user.save()

        if self.instance.coupon_code:
            self.instance.coupon_code.count -= 1
            self.instance.coupon_code.save()

        return self.instance


class QualificationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    previous_position = forms.ChoiceField(
        choices=[
            ('9', 'GRANDMASTER'),
            ('8', 'MASTER'),
            ('7', 'DIAMOND'),
            ('6', 'EMERALD'),
            ('5', 'PLATINUM'),
            ('4', 'GOLD'),
            ('3', 'SILVER'),
            ('2', 'BRONZE'),
            ('1', 'IRON'),
            ('0', 'UNRANKED'),
        ],
        widget=forms.Select(attrs={'id': 'current-position'}),
    )
    specific_role = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={'class': 'checkbox', 'type': 'checkbox', 'id': 'specific-role', 'value': '1.2'}
        ),
        required=False,
    )
    duo_booster = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={'class': 'checkbox', 'type': 'checkbox', 'id': 'duo-booster', 'value': '1.3'}
        ),
        required=False,
    )
    server = forms.ChoiceField(
        choices=[('1', 'EU WEST'), ('0.8', 'RUSSIA')], widget=forms.Select(attrs={'id': 'server'})
    )
    queue_type = forms.ChoiceField(
        choices=[('0', 'SOLO/DUO'), ('1', 'FLEX')], widget=forms.Select(attrs={'id': 'queue-type'})
    )
    coupon_code = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'coupon-code', 'placeholder': 'Ввести купон'}),
        required=False,
    )
    game_count = forms.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        widget=forms.NumberInput(
            attrs={
                'class': 'gamecount',
                'type': 'range',
                'id': 'gameSlider',
                'name': 'gameSlider',
                'min': '1',
                'max': '5',
                'value': '1',
                'step': '1',
                'oninput': 'updateGameCount(this.value)',
            }
        ),
    )
    total_time = forms.DurationField(
        widget=forms.TextInput(attrs={'id': 'total-time-form', 'class': 'hidden'}), required=False
    )
    total_price = forms.IntegerField(
        widget=forms.TextInput(attrs={'id': 'total-price-form', 'class': 'hidden'}), required=False
    )
    user = forms.CharField(
        required=False,
    )

    class Meta:
        model = Qualification
        fields = {
            'previous_position',
            'specific_role',
            'duo_booster',
            'server',
            'queue_type',
            'coupon_code',
            'game_count',
            'total_time',
            'total_price',
            'user',
        }

    def clean(self):
        cleaned_data = super().clean()

        if self.request and self.request.user.is_authenticated:
            cleaned_data['user'] = self.request.user
        else:
            raise forms.ValidationError('Пользователь не авторизован или отсутствует.')

        coupon = cleaned_data.pop('coupon_code')
        if coupon:
            status, message, _ = check_coupon(coupon, cleaned_data['user'])
            if status:
                cleaned_data['coupon_code'] = Coupon.objects.get(name=coupon)
            else:
                raise forms.ValidationError(message)

        if cleaned_data['total_time'].total_seconds() == 0:
            raise forms.ValidationError('Время не может быть равно 0, где-то ошибка')

        if cleaned_data['total_price'] != calculate_qualification(cleaned_data):
            raise forms.ValidationError('Цена не совпадает, где-то ошибка')

        cleaned_data['previous_position'] = PRE_POSITION[cleaned_data['previous_position']]
        cleaned_data['server'] = SERVER_CHOICE[cleaned_data['server']]
        cleaned_data['queue_type'] = QUEUE[cleaned_data['queue_type']]

        if cleaned_data['user'].balance < cleaned_data['total_price']:
            raise forms.ValidationError('Пополните баланс')

        return cleaned_data

    def save(self, commit=True):
        super().save(commit=True)
        user = self.request.user
        user.balance -= self.instance.total_price
        user.save()

        if self.instance.coupon_code:
            self.instance.coupon_code.count -= 1
            self.instance.coupon_code.save()

        return self.instance


class SkinsOrderForm(forms.ModelForm):
    char_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'char1name'}), required=False)

    skin_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'skin1name'}), required=False)

    user = forms.CharField(
        required=False,
    )

    server = forms.ChoiceField(
        choices=[('EU WEST', 'EU WEST'), ('RUSSIA', 'RUSSIA')],
        widget=forms.Select(attrs={'class': 'server1'}),
    )
    account_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'account_name1'}))

    price_char = forms.IntegerField(required=False)
    price_skin = forms.IntegerField(required=False)

    class Meta:
        model = SkinsOrder
        fields = {
            'char_name',
            'skin_name',
            'user',
            'price_char',
            'price_skin',
            'server',
            'account_name',
        }

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['user'] = self.request.user
        if cleaned_data.get('char_name'):
            json_path = os.path.join(settings.BASE_DIR, 'static', 'chars', 'assets', 'name2price.json')
            with open(json_path, encoding='utf-8') as file:
                json_data = json.load(file)
            cleaned_data['price_char'] = json_data[cleaned_data.get('char_name')]
            if cleaned_data.get('user').balance < cleaned_data.get('price_char'):
                raise forms.ValidationError('Пополните баланс')

        if cleaned_data.get('skin_name'):
            json_path = os.path.join(settings.BASE_DIR, 'static', 'chars', 'assets', 'skins2price.json')
            with open(json_path, encoding='utf-8') as file:
                json_data = json.load(file)
            cleaned_data['price_skin'] = json_data[cleaned_data.get('skin_name')]
            if cleaned_data.get('user').balance < cleaned_data.get('price_skin'):
                raise forms.ValidationError('Пополните баланс')

        return cleaned_data

    def save(self, commit=True):
        super().save(commit=True)
        user = self.request.user
        user.balance -= self.instance.price_skin or self.instance.price_char
        user.save()

        return self.instance


class RPorderForm(forms.ModelForm):
    rp = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'id': 'get-rp',
                'placeholder': 'Введите RP',
                'type': 'number',
                'oninput': 'convertCurrency()',
            }
        ),
        min_value=0,
    )
    price_rub = forms.IntegerField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'id': 'pay-rubles',
                'placeholder': 'Стоимость в рублях',
                'oninput': 'convertFromRubles()',
            }
        ),
    )

    server = forms.ChoiceField(
        choices=[('EU WEST', 'EU WEST'), ('RUSSIA', 'RUSSIA')],
        widget=forms.Select(attrs={'id': 'server'}),
    )
    account_name = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'character-nickname', 'placeholder': 'Введите ник'})
    )

    class Meta:
        model = RPorder
        fields = {
            'rp',
            'price_rub',
            'server',
            'account_name',
        }

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['price_rub'] = round(cleaned_data['rp'] * 0.23)
        user = self.request.user

        if cleaned_data['price_rub'] <= user.balance:
            return cleaned_data
        raise forms.ValidationError('Пополните баланс')

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        if user:
            instance.user = user
            user.balance -= self.instance.price_rub
            user.save()
        if commit:
            instance.save()
        return instance


class AccountObjectForm(forms.ModelForm):
    server = forms.ChoiceField(
        choices=[('EU WEST', 'EU WEST'), ('RUSSIA', 'RUSSIA')],
        widget=forms.Select(attrs={'id': 'server'}),
    )

    lvl = forms.IntegerField(widget=forms.NumberInput(attrs={}))
    champions = forms.IntegerField(widget=forms.NumberInput(attrs={}))
    skins = forms.IntegerField(widget=forms.NumberInput(attrs={}))
    rang = forms.ChoiceField(
        choices=[
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
    )
    short_description = forms.CharField(widget=forms.TextInput(attrs={}))
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'description',
                'rows': 4,
                'cols': 50,
                'placeholder': 'Введите полное описание здесь...',
            }
        )
    )
    price = forms.IntegerField(widget=forms.TextInput(attrs={'id': 'total-price-form'}))

    class Meta:
        model = AccountObject
        fields = [
            'server',
            'lvl',
            'champions',
            'skins',
            'rang',
            'short_description',
            'description',
            'price',
        ]

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        if user:
            instance.user = user  # Устанавливаем пользователя перед сохранением
        if commit:
            instance.save()
        return instance


class ReviewsSellerForm(forms.ModelForm):
    stars = forms.ChoiceField(
        choices=[
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
        ],
        widget=forms.TextInput(attrs={'class': 'star-input'}),
        required=False,
    )
    reviews = forms.CharField(
        widget=forms.Textarea(
            attrs={'class': 'feedback-text', 'placeholder': 'Напишите свой отзыв здесь...'}
        )
    )
    buyer = forms.CharField(required=False)

    seller = forms.CharField(required=False)

    parent = forms.CharField(widget=forms.TextInput(attrs={'class': 'parent'}), required=False)

    product = forms.CharField(required=False)

    class Meta:
        model = ReviewSellerModel
        fields = ('stars', 'reviews', 'seller', 'buyer', 'parent', 'product')

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['seller'] = self.product.user
        cleaned_data['product'] = self.product

        if cleaned_data['parent'] == '':
            cleaned_data.pop('parent')
            cleaned_data['buyer'] = self.request.user
        else:
            cleaned_data['parent'] = ReviewSellerModel.objects.get(id=cleaned_data['parent'])
            cleaned_data.pop('buyer')
        return cleaned_data


class AccountsFilterForm(forms.Form):
    server = forms.ChoiceField(
        choices=[('', 'Любой'), ('EU WEST', 'EU WEST'), ('RUSSIA', 'RUSSIA')],
        required=False,
        widget=forms.Select(attrs={'id': 'server'}),
    )
    rank = forms.ChoiceField(
        choices=[
            ('', 'Любой'),
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
        ],
        required=False,
        widget=forms.Select(attrs={'id': 'rank'}),
    )
    champions_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            attrs={'id': 'champions_min', 'name': 'champions_min', 'placeholder': 'От'}
        ),
    )
    champions_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            attrs={'id': 'champions_max', 'name': 'champions_max', 'placeholder': 'До'}
        ),
    )
    price_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'id': 'price_min', 'name': 'price_min', 'placeholder': 'От'}),
    )
    price_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'id': 'price_max', 'name': 'price_max', 'placeholder': 'До'}),
    )

    class Meta:
        fields = ['server', 'rank', 'champions_min', 'champions_max', 'price_min', 'price_max']

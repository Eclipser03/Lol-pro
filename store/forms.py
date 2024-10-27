from django import forms

from store.models import BoostOrder, Coupon
from store.services import calculate_boost

position = {
    '8' : 'GRANDMASTER',
    '7' : 'MASTER',
    '6' : 'DIAMOND',
    '5' : 'EMERALD',
    '4' : 'PLATINUM',
    '3' : 'GOLD',
    '2' : 'SILVER',
    '1' : 'BRONZE',
    '0' : 'IRON'
}

division = {
    '3' : 'DIVISION 4',
    '2' : 'DIVISION 3',
    '1' : 'DIVISION 2',
    '0' : 'DIVISION 1'
}

lp = {
    '0': '0-20LP',
    '1': '21-40LP',
    '2': '41-60LP',
    '3': '61-80LP',
    '4': '81-99LP'
}

lp_win = {
    '1': '18+LP',
    '1.1': '15-17LP',
    '1.2': '<15LP'
}

server_choice = {
    '1': 'EU WEST',
    '0.8': 'RUSSIA'
}

queue = {
    '0': 'SOLO/DUO',
    '1': 'FLEX'
}


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
        print('clean data', cleaned_data)

        coupon = cleaned_data.pop('coupon_code')
        if coupon:
            cleaned_data['coupon_code'] = Coupon.objects.get(name=coupon)


        if int(cleaned_data['current_position']) > int(cleaned_data['desired_position']):
            raise forms.ValidationError('Текущая позиция не может быть больше желаемой')

        if cleaned_data['current_position'] == cleaned_data['desired_position'] and int(
            cleaned_data['current_division']
        ) <= int(cleaned_data['desired_division']):
            raise forms.ValidationError('Текущий дивизион не может быть больше желаемого')

        if cleaned_data['total_time'].total_seconds() == 0:
            raise forms.ValidationError('Время не может быть равно 0, где-то ошибка')

        if cleaned_data['total_price'] != calculate_boost(cleaned_data):
            raise forms.ValidationError('Цена не совпадает, где-то ошибка')

        cleaned_data['current_position'] = position[cleaned_data['current_position']]
        cleaned_data['current_division'] = division[cleaned_data['current_division']]
        cleaned_data['current_lp'] = lp[cleaned_data['current_lp']]
        cleaned_data['desired_position'] = position[cleaned_data['desired_position']]
        cleaned_data['desired_division'] = division[cleaned_data['desired_division']]
        cleaned_data['lp_per_win'] = lp_win[cleaned_data['lp_per_win']]
        cleaned_data['server'] = server_choice[cleaned_data['server']]
        cleaned_data['queue_type'] = queue[cleaned_data['queue_type']]
        cleaned_data['user'] = self.request.user
        print(cleaned_data['user'])

        return cleaned_data

# {# 'total_price': 2000}
# class QualificationForm(forms.ModelForm):

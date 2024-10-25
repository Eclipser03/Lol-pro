from django import forms

from store.models import BoostOrder


class BoostOrderForms(forms.ModelForm):
    current_position = forms.ChoiceField(
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
        )
    )
    duo_booster = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={'class': 'checkbox', 'type': 'checkbox', 'id': 'duo-booster', 'value': '1.3'}
        )
    )
    coupon_code = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'coupon-code', 'placeholder': 'Ввести купон'})
    )
    total_time = forms.DurationField(widget=forms.TextInput(attrs={'id': 'total-time-form', 'class':'hidden'}))
    total_price = forms.IntegerField(widget=forms.TextInput(attrs={'id': 'total-price-form', 'class':'hidden'}))

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
        }

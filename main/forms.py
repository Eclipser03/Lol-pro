from typing import Any

from django import forms
from django.core.validators import MaxLengthValidator

from main.models import ReviewModel


class ReviewsForm(forms.ModelForm):
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
        ),
        max_length=300,  # Ограничение на уровне интерфейса
        validators=[MaxLengthValidator(300)],
    )
    user = forms.CharField(required=False)

    parent = forms.CharField(widget=forms.TextInput(attrs={'class': 'parent'}), required=False)

    class Meta:
        model = ReviewModel
        fields = ('stars', 'reviews', 'user', 'parent')

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        cleaned_data['user'] = self.request.user
        if cleaned_data['parent'] == '':
            cleaned_data.pop('parent')
        else:
            cleaned_data['parent'] = ReviewModel.objects.get(id=cleaned_data['parent'])
        return cleaned_data

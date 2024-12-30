from typing import Any

from django import forms
from django.core.validators import MaxLengthValidator
from django.shortcuts import get_object_or_404

from main.choices import ReviewsStarsChoices
from main.models import ReviewModel


class ReviewsForm(forms.ModelForm):
    stars = forms.ChoiceField(
        choices=ReviewsStarsChoices.choices,
        widget=forms.TextInput(attrs={'class': 'star-input'}),
        required=False,
    )
    reviews = forms.CharField(
        widget=forms.Textarea(
            attrs={'class': 'feedback-text', 'placeholder': 'Напишите свой отзыв здесь...'}
        ),
        max_length=300,
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

        parent_pk = cleaned_data.pop('parent', None)
        if parent_pk:
            cleaned_data['parent'] = get_object_or_404(ReviewModel, pk=parent_pk)
            cleaned_data['stars'] = None
        return cleaned_data

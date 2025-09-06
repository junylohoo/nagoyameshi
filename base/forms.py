# forms.py
from django import forms
from base.models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["title", "content", "rating"]

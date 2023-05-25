from .models import Comment, City
from django import forms
from django.forms import ModelForm, TextInput


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)


class CityForm(ModelForm):
    class Meta:
        model = City
        fields = ['name']
        widgets = {
            'name': TextInput(attrs={'class': 'input', 'placeholder': 'City Name'}),
        }




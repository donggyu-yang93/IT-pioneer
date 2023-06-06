from .models import Comment, City, Post
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

class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['rcp_name', 'large_img', 'small_img', 'ingredient', 'manual01', 'manual02', 'manual03', 'manual04', 'manual05', 'manual06', 'category']


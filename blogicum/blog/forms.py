from django import forms
from django.contrib.auth import get_user_model

from .models import Post, Congratulation


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author', 'is_published')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email')


class CongratulationForm(forms.ModelForm):
    class Meta:
        model = Congratulation
        fields = ('text',)

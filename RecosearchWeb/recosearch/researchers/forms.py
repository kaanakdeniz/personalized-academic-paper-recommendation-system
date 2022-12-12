from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import Article, ArticleGroup


class CreateUserForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control form-control-user',
                'placeholder': f'{field.label}'
            })

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password1', 'password2']


class CreateArticleGroupForm(ModelForm):

    class Meta:
        model = ArticleGroup
        fields = ['groupname']
        widgets = {
            'groupname': forms.TextInput(attrs={'class': 'form-control'}),
        }


# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm, Form
from django.contrib.auth.models import User

class LoginForm(Form):
    username = forms.CharField(max_length=30, label='Identifiant :', required=True)
    password = forms.CharField(max_length=30, label='Mot de passe :', required=True, widget=forms.PasswordInput)


class UserCreationForm(ModelForm):
    username = forms.CharField(max_length=30, label='Identifiant :', required=True)
    last_name = forms.CharField(max_length=30, label='Nom :', required=False)
    first_name = forms.CharField(max_length=30, label='Prénom :', required=False)
    password = forms.CharField(max_length=30, label='Mot de passe :', required=True)
    is_active = forms.ChoiceField(label='Actif :', choices=((0, 'Non'), (1, 'Oui')), widget=forms.Select)
    is_staff = forms.ChoiceField(label='Admin :', choices=((0, 'Non'), (1, 'Oui')), widget=forms.Select)

    class Meta:
        model = User
        fields = ('username', 'last_name', 'first_name', 'password', 'is_active', 'is_staff')


class UserEditionForm(ModelForm):
    username = forms.CharField(max_length=30, label='Identifiant :', required=True)
    last_name = forms.CharField(max_length=30, label='Nom :', required=False)
    first_name = forms.CharField(max_length=30, label='Prénom :', required=False)
    is_active = forms.ChoiceField(label='Actif :', choices=((0, 'Non'), (1, 'Oui')), widget=forms.Select)
    is_staff = forms.ChoiceField(label='Admin :', choices=((0, 'Non'), (1, 'Oui')), widget=forms.Select)

    class Meta:
        model = User
        fields = ('username', 'last_name', 'first_name', 'is_active', 'is_staff')


class UserPasswordForm(ModelForm):
    password = forms.CharField(max_length=30, label='Mot de passe :', required=True)

    class Meta:
        model = User
        fields = ('password',)
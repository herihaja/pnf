# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm, Form

from guichets.models import Guichet

class GuichetForm(ModelForm):
    class Meta:
        model = Guichet

class FiltreGuichetForm(Form):
    nom = forms.CharField(max_length=40, required=False)
    page = forms.CharField(widget=forms.HiddenInput(), initial=1)
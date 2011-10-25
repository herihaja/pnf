# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm, Form

from bailleurs.models import Bailleur

class BailleurForm(ModelForm):
    class Meta:
        model = Bailleur

class FiltreBailleurForm(Form):
    nom = forms.CharField(max_length=40, required=False)
    page = forms.CharField(widget=forms.HiddenInput(), initial=1)
# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm, Form
from compteur.models import Compteur, CHOIX_OPERATEUR


class CompteurForm(ModelForm):
    class Meta:
        model = Compteur


class CompteurRechargeForm(ModelForm):
    recharge = forms.CharField(max_length=10)
    class Meta:
        model = Compteur
        exclude= ("prix, credit, operateur")

# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm, Form
from projets.models import Projet
from bailleurs.models import Bailleur

class ProjetForm(ModelForm):
    class Meta:
        model = Projet

class FiltreProjetForm(Form):
    nom = forms.CharField(max_length=80, required=False)
    bailleurs = forms.ModelChoiceField(label='Bailleur', queryset=Bailleur.objects.all(), required=False)
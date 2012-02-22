# -*- coding: utf-8 -*-
import datetime
from django import forms
from django.forms import Form
from localites.models import Region

class FiltreRatioForm(Form):
    LISTE_ANNEE = ((str(i), str(i)) for i in range(2009, datetime.datetime.now().year))
    annee = forms.ChoiceField(label='Année', choices=LISTE_ANNEE, required=False)
    region = forms.ModelChoiceField(label='Régions', queryset=Region.objects.all(), required=False)

class FiltreRMAForm(Form):
    region = forms.ModelChoiceField(label='Régions', queryset=Region.objects.all(), required=False)
    periode = forms.CharField(label='Période', required=False)
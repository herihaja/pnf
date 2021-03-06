# -*- coding: utf-8 -*-
import datetime
from django import forms
from django.forms import Form
from localites.models import Region

class FiltreForm(Form):
    LISTE_ANNEE = ((str(i), str(i)) for i in range(2006, datetime.datetime.now().year+1))
    annee = forms.ChoiceField(label='Année', choices=LISTE_ANNEE, required=False)
    region = forms.ModelChoiceField(label='Régions', queryset=Region.objects.all(), required=False)

class FiltreRatioForm(Form):
    LISTE_ANNEE = ((str(i), str(i)) for i in range(2006, datetime.datetime.now().year+1))
    LISTE_INDICATEURS = (
                ('0', 'Certification'),
                ('1', 'Certificats à des femmes'),
                ('2', 'Conflictualité'),
                ('3', 'Résolution'),
            )
    indicateur = forms.ChoiceField(label='Indicateur', choices=LISTE_INDICATEURS, required=False)
    annee = forms.ChoiceField(label='Année', choices=LISTE_ANNEE, required=False)
    region = forms.ModelChoiceField(label='Régions', queryset=Region.objects.all(), required=False)

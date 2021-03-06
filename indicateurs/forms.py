# -*- coding: utf-8 -*-
import datetime
from django import forms
from django.forms import ModelForm, Form
from localites.models import Region, District, Commune

EMPTY_LIST = (('', '---'),)
class FiltreIndicateursForm(Form):
    region = forms.ModelChoiceField(label='Région', queryset=Region.objects.all(), required=False)
    district = forms.ChoiceField(label='District', choices=EMPTY_LIST, required=False)
    commune = forms.ChoiceField(label='Commune', choices=EMPTY_LIST, required=False)
    code = forms.CharField(max_length=6, required=False)
    date_de = forms.CharField(label='Entre', required=False)
    date_a = forms.CharField(label='et', required=False)

class FiltreIndicateurForm(Form):
    LISTE_ANNEE = ((str(i), str(i)) for i in range(2006, datetime.datetime.now().year+1))
    LISTE_INDICATEURS = (
            ('demandes', 'Demandes'),
            ('oppositions', 'Oppositions'),
            ('resolues', 'Résolues'),
            ('certificats', 'Certificats'),
            ('femmes', 'Certificats femmes'),
            ('recettes', 'Recettes'),
            ('mutations', 'Mutations'),
            ('surfaces', 'Surfaces'),
            ('garanties', 'Garanties'),
        )

    indicateur = forms.ChoiceField(label='Indicateur', choices=LISTE_INDICATEURS, required=False)
    annee = forms.ChoiceField(label='Année', choices=LISTE_ANNEE, required=False)
    region = forms.ModelChoiceField(label='Régions', queryset=Region.objects.all(), required=False)
    district = forms.ChoiceField(label='District', choices=EMPTY_LIST, required=False)
    commune = forms.ChoiceField(label='Commune', choices=EMPTY_LIST, required=False)
    code = forms.CharField(max_length=6, required=False)

class FiltreRatioForm(Form):
    LISTE_ANNEE = ((str(i), str(i)) for i in range(2006, datetime.datetime.now().year+1))
    LISTE_INDICATEURS = (
            ('rcertificats', 'Certification'),
            ('rfemmes', 'Certificats à des femmes'),
            ('rconflits', 'Conflictualité'),
            ('rresolus', 'Résolution'),
            ('rsurface', 'Surface moyen'),
        )
    indicateur = forms.ChoiceField(label='Indicateur', choices=LISTE_INDICATEURS, required=False)
    annee = forms.ChoiceField(label='Année', choices=LISTE_ANNEE, required=False)
    region = forms.ModelChoiceField(label='Régions', queryset=Region.objects.all(), required=False)
    district = forms.ChoiceField(label='District', choices=EMPTY_LIST, required=False)
    commune = forms.ChoiceField(label='Commune', choices=EMPTY_LIST, required=False)
    code = forms.CharField(max_length=6, required=False)

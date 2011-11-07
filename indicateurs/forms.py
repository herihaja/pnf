# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm, Form
from localites.models import Region, District, Commune

class FiltreIndicateursForm(Form):
    region = forms.ModelChoiceField(label='Région', queryset=Region.objects.all(), required=False)
    district = forms.ModelChoiceField(label='District', queryset=District.objects.all(), required=False)
    commune = forms.ModelChoiceField(label='Commune', queryset=Commune.objects.all(), required=False)
    date_de = forms.CharField(label='Entre', required=False)
    date_a = forms.CharField(label='et', required=False)

class FiltreIndicateurForm(Form):
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
    LISTE_ANNEE = ((str(i), str(i)) for i in range(2009, 2020))
    indicateur = forms.ChoiceField(label='Indicateur', choices=LISTE_INDICATEURS, required=False)
    annee = forms.ChoiceField(label='Année', choices=LISTE_ANNEE, required=False)
    region = forms.ModelChoiceField(label='Régions', queryset=Region.objects.all(), required=False)
    district = forms.ModelChoiceField(label='District', queryset=District.objects.all(), required=False)
    commune = forms.ModelChoiceField(label='Commune', queryset=Commune.objects.all(), required=False)
    valide = forms.CharField(widget=forms.HiddenInput(), initial=1)

class FiltreRatioForm(Form):
    LISTE_INDICATEURS = (
            ('rcertificats', 'Certification'),
            ('rfemmes', 'Certificats à des femmes'),
            ('rconflits', 'Conflictualité'),
            ('rresolus', 'Résolution'),
            ('rsurface', 'Surface moyen'),
        )
    LISTE_ANNEE = ((str(i), str(i)) for i in range(2009, 2020))
    indicateur = forms.ChoiceField(label='Indicateur', choices=LISTE_INDICATEURS, required=False)
    annee = forms.ChoiceField(label='Année', choices=LISTE_ANNEE, required=False)
    region = forms.ModelChoiceField(label='Régions', queryset=Region.objects.all(), required=False)
    district = forms.ModelChoiceField(label='District', queryset=District.objects.all(), required=False)
    commune = forms.ModelChoiceField(label='Commune', queryset=Commune.objects.all(), required=False)
    valide = forms.CharField(widget=forms.HiddenInput(), initial=1)
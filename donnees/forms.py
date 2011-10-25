# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm, Form
from donnees.models import Donnees
from localites.models import Region, District, Commune

class DonneesForm(ModelForm):
    class Meta:
        model = Donnees
        

class FiltreDonneesForm(Form):
    code = forms.CharField(max_length=6, required=False)
    region = forms.ModelChoiceField(label='Région', queryset=Region.objects.all(), required=False)
    district = forms.ModelChoiceField(label='District', queryset=District.objects.all(), required=False)
    commune = forms.ModelChoiceField(label='Commune', queryset=Commune.objects.all(), required=False)
    demandes = forms.CharField(required=False)
    oppositions = forms.CharField(required=False)
    resolues = forms.CharField(required=False)
    certificats = forms.CharField(required=False)
    femmes = forms.CharField(required=False)
    recettes = forms.CharField(required=False)
    mutations = forms.CharField(required=False)
    surfaces = forms.CharField(required=False)
    garanties = forms.CharField(required=False)
    periode_de_annee = forms.CharField(required=False)
    periode_a_annee = forms.CharField(required=False)
    periode_de_mois = forms.CharField(required=False)
    periode_a_mois = forms.CharField(required=False)
    page = forms.CharField(widget=forms.HiddenInput(), initial=1)
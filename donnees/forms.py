# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm, Form
from donnees.models import Donnees
from localites.models import Region, District, Commune

class DonneesForm(ModelForm):
    class Meta:
        model = Donnees
        

class FiltreDonneesForm(Form):
    region = forms.ModelChoiceField(label='Région', queryset=Region.objects.all(), required=False)
    district = forms.ModelChoiceField(label='District', queryset=District.objects.all(), required=False)
    commune = forms.ModelChoiceField(label='Commune', queryset=Commune.objects.all(), required=False)
    code = forms.CharField(max_length=6, required=False, widget=forms.TextInput(attrs={'style':'width:60px;'}))
    demandes = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 60px;'}))
    oppositions = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 60px;'}))
    resolues = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 60px;'}))
    certificats = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 60px;'}))
    femmes = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 60px;'}))
    recettes = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 60px;'}))
    mutations = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 60px;'}))
    surfaces = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 60px;'}))
    garanties = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 60px;'}))
    periode_de_annee = forms.CharField(label='De année', required=False)
    periode_de_mois = forms.CharField(label='mois', required=False)
    periode_a_annee = forms.CharField(label='A année', required=False)
    periode_a_mois = forms.CharField(label='mois', required=False)
    page = forms.CharField(widget=forms.HiddenInput(), initial=1)
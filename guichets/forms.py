# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm, Form
from bailleurs.models import Bailleur
from guichets.models import Guichet
from localites.models import Region, District, Commune

class GuichetForm(ModelForm):
    class Meta:
        model = Guichet

class FiltreGuichetForm(Form):
    CHOIX_ETAT = (
        ('', '---'),
        ('1', 'Actif'),
        ('2', 'Non actif'),
        ('3', 'Fermé'),
        ('4', 'En cours'),
    )
    region = forms.ModelChoiceField(label='Région', queryset=Region.objects.all(), required=False)
    district = forms.ModelChoiceField(label='District', queryset=District.objects.all(), required=False)
    commune = forms.ModelChoiceField(label='Commune', queryset=Commune.objects.all(), required=False)
    code_commune = forms.CharField(label='Code com', max_length=6, required=False)
    etat = forms.ChoiceField(label='Etat', choices=CHOIX_ETAT, required=False)
    agf1 = forms.CharField(required=False)
    mobile1 = forms.CharField(required=False)
    cree_de = forms.DateField(required=False)
    cree_a = forms.DateField(required=False)
    bailleur = forms.ModelChoiceField(label='Bailleur', queryset=Bailleur.objects.all(), required=False)
    page = forms.CharField(widget=forms.HiddenInput(), initial=1)
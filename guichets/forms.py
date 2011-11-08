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
    code = forms.CharField(label='Code com', max_length=6, required=False)
    agf1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 80px;'}))
    mobile1 = forms.CharField(required=False)
    agf2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 80px;'}))
    mobile2 = forms.CharField(required=False)
    etat = forms.ChoiceField(label='Etat', choices=CHOIX_ETAT, required=False)
    creede = forms.DateField(label='Créé entre', required=False)
    creea = forms.DateField(label='et', required=False)
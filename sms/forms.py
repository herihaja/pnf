# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm, Form
from localites.models import Region

EMPTY_LIST = (('', '---'),)
class FiltreReceptionForm(Form):
    expediteur = forms.CharField(label='Expéditeur', max_length=30, required=False)
    message = forms.CharField(label='Message', max_length=60, required=False)
    statut = forms.CharField(widget=forms.HiddenInput(), required=False)
    cree_de = forms.DateField(label='Reçu entre le', required=False)
    cree_a = forms.DateField(label='et le', required=False)

class FiltreEnvoiForm(Form):
    destinataire = forms.CharField(label='Destinataire', max_length=30, required=False)
    message = forms.CharField(label='Message', max_length=60, required=False)
    cree_de = forms.DateField(label='Envoyé du', required=False)
    cree_a = forms.DateField(label='au', required=False)

class TesterForm(Form):
    expediteur = forms.CharField(label='Expéditeur', max_length=20, required=True)
    message = forms.CharField(label='Message', widget=forms.Textarea, required=True)

class BroadcastForm(Form):
    region = forms.ModelChoiceField(label='Région', queryset=Region.objects.all(), required=False)
    district = forms.ChoiceField(label='District', choices=EMPTY_LIST, required=False)
    commune = forms.ChoiceField(label='Commune', choices=EMPTY_LIST, required=False)
    liste = forms.CharField(label='Destinataire', max_length=200, required=False)
    destinataire = forms.CharField(label='Destinataire', required=True, widget=forms.HiddenInput())
    message = forms.CharField(label='Message', widget=forms.Textarea, required=True)

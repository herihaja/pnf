# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm, Form

class FiltreReceptionForm(Form):
    CHOIX_STATUT = (
        ('', '---'),
        ('1', 'Validé'),
        ('2', 'Inconnu'),
        ('3', 'Erreur'),
    )

    expediteur = forms.CharField(label='Expéditeur', max_length=6, required=False)
    message = forms.CharField(label='Message', max_length=6, required=False)
    statut = forms.ChoiceField(label='Etat', choices=CHOIX_STATUT, required=False)
    cree_de = forms.DateField(label='Reçu entre le', required=False)
    cree_a = forms.DateField(label='et le', required=False)

class FiltreEnvoiForm(Form):
    destinataire = forms.CharField(label='Destinataire', max_length=6, required=False)
    message = forms.CharField(label='Message', max_length=6, required=False)
    date_envoi_de = forms.DateField(label='Envoyé entre le', required=False)
    date_envoi_a = forms.DateField(label='et le', required=False)
    page = forms.CharField(widget=forms.HiddenInput(), initial=1)

class TesterForm(Form):
    expediteur = forms.CharField(label='Expéditeur', max_length=20, required=True)
    message = forms.CharField(label='Message', widget=forms.Textarea, required=True)

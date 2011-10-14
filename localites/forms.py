# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm, Form
from localites.models import Province, Region, District, Commune

class ProvinceForm(ModelForm):
    class Meta:
        model = Province

class RegionForm(ModelForm):
    class Meta:
        model = Region

class DistrictForm(ModelForm):
    class Meta:
        model = District

class CommuneForm(ModelForm):
    class Meta:
        model = Commune

class FiltreDistrictForm(Form):
    nom = forms.CharField(max_length=40, required=False)
    code = forms.CharField(max_length=6, required=False)
    region = forms.ModelChoiceField(label='Région', queryset=Region.objects.all(), required=False)
    page = forms.CharField(widget=forms.HiddenInput(), initial=1)

class FiltreCommuneForm(Form):
    nom = forms.CharField(max_length=40, required=False)
    code = forms.CharField(max_length=6, required=False)
    region = forms.ModelChoiceField(label='Région', queryset=Region.objects.all(), required=False)
    district = forms.ModelChoiceField(label='District', queryset=District.objects.all(), required=False)
    page = forms.CharField(widget=forms.HiddenInput(), initial=1)
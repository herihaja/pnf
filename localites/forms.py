# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm, Form
from localites.models import Province, Region, District, Commune
EMPTY_LIST = (('', '---'),)
class ProvinceForm(ModelForm):
    class Meta:
        model = Province
        exclude= ("slug")

class RegionForm(ModelForm):
    class Meta:
        model = Region
        exclude= ("slug")

class DistrictForm(ModelForm):
    class Meta:
        model = District
        exclude= ("slug")

class CommuneForm(ModelForm):
    region = forms.ModelChoiceField(label='Région', queryset=Region.objects.all(), required=False)
    district = forms.ModelChoiceField(label='District', queryset=District.objects.all(), required=False)
    class Meta:
        model = Commune
        fields = ('region', 'district', 'nom', 'code')

    def __init__(self, *args, **kwargs):
        region_id = kwargs.pop('region_id', None)
        super(CommuneForm, self).__init__(*args, **kwargs)
        if region_id:
            self.fields['district'].queryset = District.objects.filter(region=region_id)

class FiltreDistrictForm(Form):
    district = forms.CharField(max_length=40, required=False)
    code = forms.CharField(max_length=6, required=False)
    region = forms.ModelChoiceField(label='Région', queryset=Region.objects.all(), required=False)

class FiltreCommuneForm(Form):
    nom = forms.CharField(max_length=40, required=False)
    code = forms.CharField(max_length=6, required=False)
    region = forms.ModelChoiceField(label='Région', queryset=Region.objects.all(), required=False)
    district = forms.ChoiceField(label='District', choices=EMPTY_LIST, required=False)
# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm, Form
from donnees.models import Donnees, Recu
from localites.models import Region, District, Commune

EMPTY_LIST = (('', '---'),)
class DonneesForm(ModelForm):
    region = forms.ModelChoiceField(label='Région', queryset=Region.objects.all(), required=False)
    district = forms.ModelChoiceField(label='District', queryset=District.objects.all(), required=False)
    commune = forms.ModelChoiceField(label='Commune', queryset=Commune.objects.all(), required=False)
    class Meta:
        model = Donnees
        fields = ('region', 'district', 'commune', 'periode', 'demandes', 'oppositions', 'resolues',
            'certificats', 'femmes', 'reconnaissances', 'recettes', 'mutations', 'surfaces', 'garanties')

    def __init__(self, *args, **kwargs):
        region_id = kwargs.pop('region_id', None)
        district_id = kwargs.pop('district_id', None)
        super(DonneesForm, self).__init__(*args, **kwargs)
        if region_id:
            self.fields['district'].queryset = District.objects.filter(region=region_id)
            self.fields['commune'].queryset = Commune.objects.filter(district=district_id)
        

class FiltreDonneesForm(Form):
    region = forms.ModelChoiceField(label='Région', queryset=Region.objects.all(), required=False)
    district = forms.ChoiceField(label='District', choices=EMPTY_LIST, required=False)
    commune = forms.ChoiceField(label='Commune', choices=EMPTY_LIST, required=False)
    code = forms.CharField(max_length=6, required=False)
    demandes = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 60px;'}))
    oppositions = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 60px;'}))
    resolues = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 60px;'}))
    certificats = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 60px;'}))
    femmes = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 60px;'}))
    reconnaissances = forms.CharField(label='Reco', required=False, widget=forms.TextInput(attrs={'style':'width: 60px;'}))
    recettes = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 60px;'}))
    mutations = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 60px;'}))
    surfaces = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 60px;'}))
    garanties = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 60px;'}))
    periode_de = forms.CharField(label='Entre', required=False)
    periode_a = forms.CharField(label='et', required=False)

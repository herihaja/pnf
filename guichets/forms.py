# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm, Form
from bailleurs.models import Bailleur
from guichets.models import Guichet
from localites.models import Region, District, Commune

EMPTY_LIST = (('', '---'),)
class GuichetForm(ModelForm):
    region = forms.ModelChoiceField(label='Région', queryset=Region.objects.all(), required=False)
    district = forms.ModelChoiceField(label='District', queryset=District.objects.all(), required=False)
    commune = forms.ModelChoiceField(label='Commune', queryset=Commune.objects.all(), required=False)
    
    class Meta:
        model = Guichet
        fields = ('region', 'district', 'commune', 'bailleurs', 'creation', 'agf1', 'mobile1', 'password1', 'agf2', 'mobile2', 'password2', 'etat')

    def __init__(self, *args, **kwargs):
        region_id = kwargs.pop('region_id', None)
        district_id = kwargs.pop('district_id', None)
        super(GuichetForm, self).__init__(*args, **kwargs)
        if region_id:
            self.fields['district'].queryset = District.objects.filter(region=region_id)
            self.fields['commune'].queryset = Commune.objects.filter(district=district_id)

class FiltreGuichetForm(Form):
    CHOIX_ETAT = (
        ('', '---'),
        ('1', 'Actif'),
        ('2', 'Non actif'),
        ('3', 'Fermé'),
        ('4', 'En cours'),
    )
    region = forms.ModelChoiceField(label='Région', queryset=Region.objects.all(), required=False)
    district = forms.ChoiceField(label='District', choices=EMPTY_LIST, required=False)
    commune = forms.ChoiceField(label='Commune', choices=EMPTY_LIST, required=False)
    code = forms.CharField(label='Code com', max_length=6, required=False)
    agf1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 80px;'}))
    mobile1 = forms.CharField(required=False)
    agf2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width: 80px;'}))
    mobile2 = forms.CharField(required=False)
    etat = forms.ChoiceField(label='Etat', choices=CHOIX_ETAT, required=False)
    creede = forms.DateField(label='Créé entre', required=False)
    creea = forms.DateField(label='et', required=False)

class FiltreBailleurForm(Form):
    CHOIX_ETAT = (
        ('', '---'),
        ('1', 'Actif'),
        ('2', 'Non actif'),
        ('3', 'Fermé'),
        ('4', 'En cours'),
    )
    region = forms.ModelChoiceField(label='Région', queryset=Region.objects.all(), required=False)
    district = forms.ChoiceField(label='District', choices=EMPTY_LIST, required=False)
    commune = forms.ChoiceField(label='Commune', choices=EMPTY_LIST, required=False)
    code = forms.CharField(label='Code com', max_length=6, required=False)
    etat = forms.ChoiceField(label='Etat', choices=CHOIX_ETAT, required=False)
    bailleurs = forms.ModelChoiceField(label='Bailleurs', queryset=Bailleur.objects.all().order_by('nom'), required=False)
    creede = forms.DateField(label='Créé entre', required=False)
    creea = forms.DateField(label='et', required=False)
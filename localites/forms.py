from django.forms.fields import CharField, ChoiceField, MultipleChoiceField
from django.core.exceptions import ValidationError
from django.forms.forms import Form
from django.forms import ModelForm
from django import forms

from models import Province, Region, District, Commune

class ProvinceForm(ModelForm):
    class Meta:
        model = Province

class RegionForm(ModelForm):
    class Meta:
        model = Region

class DistrictForm(ModelForm):
    class Meta:
        model = Province

class CommuneForm(ModelForm):
    class Meta:
        model = Province

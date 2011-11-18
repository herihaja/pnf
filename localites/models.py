# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q, Model, Manager
from django.core.exceptions import ObjectDoesNotExist

class Province(Model):
    nom = models.CharField(max_length=20)
    code = models.CharField(max_length=6, blank=True, null=True, unique=True)
    slug = models.SlugField()

    class Meta:
        ordering = ['nom']

    def __unicode__(self):
        return self.nom

class RegionManager(Manager):
    def filter_for_xls(self):
        queryset = self.all()
        dataset = []
        for row in queryset:
            row_list = [row.nom, row.code]
            dataset.append(row_list)
        return dataset

class Region(Model):
    province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.SET_NULL)
    nom = models.CharField(max_length=20)
    code = models.CharField(max_length=6, blank=True, null=True, unique=True)
    slug = models.SlugField()

    objects = RegionManager()

    class Meta:
        ordering = ['nom']

    def __unicode__(self):
        return self.nom

class DistrictManager(Manager):
    def filter_for_xls(self, post):
        kwargs = {}
        if 'id_nom' in post and post['id_nom'] != '':
            kwargs['nom__icontains'] = str(post['id_nom'])
        if 'id_code' in post and post['id_code'] != '':
            kwargs['code__icontains'] = post['id_code']
        if 'id_region' in post and post['id_region'] != '':
            kwargs['district__region'] = post['id_region']
        queryset = self.filter(**kwargs)
        dataset = []
        for row in queryset:
            row_list = [row.nom, row.code, row.region.nom]
            dataset.append(row_list)
        return dataset

class District(Model):
    region = models.ForeignKey(Region, blank=True, null=True, on_delete=models.SET_NULL)
    nom = models.CharField(max_length=40)
    code = models.CharField(max_length=6, blank=True, null=True)
    slug = models.SlugField()

    objects = DistrictManager()

    class Meta:
        ordering = ['nom']

    def __unicode__(self):
        return self.nom

class CommuneManager(Manager):
    def filter_for_xls(self, post):
        kwargs = {}
        if 'id_nom' in post and post['id_nom'] != '':
            kwargs['nom__icontains'] = str(post['id_nom'])
        if 'id_code' in post and post['id_code'] != '':
            kwargs['code__icontains'] = post['id_code']
        if 'id_district' in post and post['id_district'] != '':
            kwargs['district'] = post['id_district']
        else:
            if 'id_region' in post and post['id_region'] != '':
                kwargs['district__region'] = post['id_region']
        queryset = self.filter(**kwargs)
        dataset = []
        for row in queryset:
            try:
                guichet = row.guichet
                guichet = guichet.get_etat_display()
            except ObjectDoesNotExist:
                guichet = 'Non'
            row_list = [row.nom, row.code, row.district.region.nom, row.district.nom, guichet]
            dataset.append(row_list)
        return dataset

class Commune(Model):
    district = models.ForeignKey(District, blank=True, null=True, on_delete=models.SET_NULL)
    nom = models.CharField(max_length=40)
    code = models.CharField(max_length=8, blank=True, null=True)
    slug = models.SlugField()

    objects = CommuneManager()

    class Meta:
        ordering = ['nom']

    def __unicode__(self):
        return '%s - %s' % (self.code, self.nom,)

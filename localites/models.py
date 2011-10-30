# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q, Model, Manager


class Province(Model):
    nom = models.CharField(max_length=20)
    code = models.CharField(max_length=6, blank=True, null=True)
    slug = models.SlugField()

    class Meta:
        ordering = ['nom']

    def __unicode__(self):
        return self.nom

class Region(Model):
    province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.SET_NULL)
    nom = models.CharField(max_length=20)
    code = models.CharField(max_length=6, blank=True, null=True)
    slug = models.SlugField()

    class Meta:
        ordering = ['nom']

    def __unicode__(self):
        return self.nom

class DistrictManager(Manager):
    def filtrer(self, post):
        qry = Q()
        nom = post.POST['nom']
        code = post.POST['code']
        region = post.POST['region']
        if len(nom) > 0:
            qry = qry & Q(nom__icontains=nom)
        if len(code) > 0:
            qry = qry & Q(code__icontains=code)
        if len(region) > 0:
            qry = qry & Q(region=int(region))

        return self.filter(qry)

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
    def filtrer(self, post):
        qry = Q()
        nom = post.POST['nom']
        code = post.POST['code']
        district = post.POST['district']
        region = post.POST['region']
        if len(nom) > 0:
            qry = qry & Q(nom__icontains=nom)
        if len(code) > 0:
            qry = qry & Q(code__icontains=code)
        if len(district) > 0:
            qry = qry & Q(district=int(district))
        if len(region) > 0:
            qry = qry & Q(district__region=int(region))

        return self.filter(qry)

class Commune(Model):
    district = models.ForeignKey(District, blank=True, null=True, on_delete=models.SET_NULL)
    nom = models.CharField(max_length=40)
    code = models.CharField(max_length=8, blank=True, null=True)
    slug = models.SlugField()

    objects = CommuneManager()

    class Meta:
        ordering = ['nom']

    def __unicode__(self):
        return self.nom

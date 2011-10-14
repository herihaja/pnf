# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q, Model, Manager

class GuichetManager(Manager):
    def filtrer(self, post):
        qry = Q()
        nom = post.POST['nom']
        if len(nom) > 0:
            qry = qry & Q(nom__icontains=nom)

        return self.filter(qry)

class Guichet(Model):
    commune = models.ForeignKey(Province, blank=True, null=True, on_delete=models.SET_NULL)
    creation = models.DateField()
    agf1 = models.CharField(max_length=6, blank=True, null=True)
    mobile1 = models.CharField(max_length=15, blank=True, null=True)
    agf2 = models.CharField(max_length=6, blank=True, null=True)
    mobile2 = models.CharField(max_length=15, blank=True, null=True)
    etat = 

    objects = GuichetManager()

    def __unicode__(self):
        return self.nom

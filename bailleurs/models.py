# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q, Model, Manager

class BailleurManager(Manager):
    def filtrer(self, post):
        qry = Q()
        nom = post.POST['nom']
        if len(nom) > 0:
            qry = qry & Q(nom__icontains=nom)

        return self.filter(qry)

class Bailleur(Model):
    nom = models.CharField(max_length=40)

    objects = BailleurManager()

    def __unicode__(self):
        return self.nom

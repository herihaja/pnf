# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q, Model, Manager
from localites.models import Commune

class GuichetManager(Manager):
    def filtrer(self, post):
        qry = Q()
        agf = post.POST['agf1']
        if len(agf) > 0:
            qry = qry & Q(agf1__icontains=agf)

        return self.filter(qry)

class Guichet(Model):
    CHOIX_ETAT = (
        ('1', 'Actif'),
        ('2', 'Non actif'),
        ('3', 'Fermé'),
        ('4', 'En cours'),
    )
    commune = models.ForeignKey(Commune, blank=True, null=True, on_delete=models.SET_NULL)
    creation = models.DateField()
    agf1 = models.CharField(max_length=6, blank=True, null=True)
    mobile1 = models.CharField(max_length=15, blank=True, null=True)
    agf2 = models.CharField(max_length=6, blank=True, null=True)
    mobile2 = models.CharField(max_length=15, blank=True, null=True)
    etat = models.CharField(max_length=1, choices=CHOIX_ETAT)
    ajout = models.DateTimeField(auto_now_add=True)
    edit = models.DateTimeField(auto_now=True)

    objects = GuichetManager()

    def __unicode__(self):
        return self.commune

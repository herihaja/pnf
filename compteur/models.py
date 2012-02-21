# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Model

CHOIX_OPERATEUR = (
            ('1', 'Airtel'),
            ('2', 'Orange'),
            ('3', 'Telma'),
        )

class Compteur(Model):
    operateur = models.CharField(max_length=1, choices=CHOIX_OPERATEUR)
    prix = models.IntegerField()
    credit = models.IntegerField()
    edit = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return 'Solde de %s sur %s' % (self.credit, self.operateur)

class Log(Model):
    CHOIX_OPERATION = (
                ('1', 'Recharge'),
                ('2', 'Ajustement'),
            )
    operateur = models.CharField(max_length=1, choices=CHOIX_OPERATEUR)
    operation = models.CharField(max_length=1, choices=CHOIX_OPERATEUR)
    credit = models.IntegerField()
    ajout = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s de %s sur %s le %s' % (self.operation, self.credit, self.operateur, self.ajout)


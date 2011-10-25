# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q, Model, Manager

class ReceptionManager(Manager):
    def filtrer(self, post):
        qry = Q()
        expediteur = post.POST['expediteur']
        message = post.POST['message']
        date_reception_de = post.POST['date_reception_de']
        date_reception_a = post.POST['date_reception_a']
        statut = post.POST['statut']
        if len(expediteur) > 0:
            qry = qry & Q(expediteur__icontains=expediteur)
        if len(message) > 0:
            qry = qry & Q(message__icontains=message)
        if len(statut) > 0:
            qry = qry & Q(statut=statut)
        if len(date_reception_de) > 0:
            qry = qry & Q(date_reception__gte=date_reception_de)
        if len(date_reception_a) > 0:
            qry = qry & Q(date_reception__lte=date_reception_a)

        return self.filter(qry)

class Reception(Model):
    CHOIX_STATUT = (
        ('1', 'Validé'),
        ('2', 'Inconnu'),
        ('3', 'Erreur'),
    )
    date_reception = models.DateTimeField()
    expediteur = models.CharField(max_length=20)
    message = models.CharField(max_length=160)
    statut = models.CharField(max_length=1, choices=CHOIX_STATUT)
    retour = models.CharField(max_length=160)
    ajout = models.DateTimeField(auto_now_add=True)

    objects = ReceptionManager()

    def __unicode__(self):
        return self.nom

class EnvoiManager(Manager):
    def filtrer(self, post):
        qry = Q()
        destinataire = post.POST['destinataire']
        message = post.POST['message']
        date_envoi_de = post.POST['date_envoi_de']
        date_envoi_a = post.POST['date_envoi_a']
        if len(destinataire) > 0:
            qry = qry & Q(destinataire__icontains=destinataire)
        if len(message) > 0:
            qry = qry & Q(message__icontains=message)
        if len(date_envoi_de) > 0:
            qry = qry & Q(date_envoi__gte=date_envoi_de)
        if len(date_envoi_a) > 0:
            qry = qry & Q(date_envoi__lte=date_envoi_a)

        return self.filter(qry)

class Envoi(Model):
    date_envoi = models.DateTimeField()
    destinataire = models.CharField(max_length=20)
    message = models.CharField(max_length=160)
    ajout = models.DateTimeField(auto_now_add=True)

    objects = EnvoiManager()

    def __unicode__(self):
        return self.nom
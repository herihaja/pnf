# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import models
from django.db.models import Q, Model, Manager

class ReceptionManager(Manager):
    def filter_for_xls(self, post):
        kwargs = {}
        if 'expediteur' in post and post['expediteur'] != '':
            kwargs['expediteur__icontains'] = str(post['expediteur'])
        if 'message' in post and post['message'] != '':
            kwargs['message__icontains'] = str(post['message'])
        if 'cree_de' in post and post['cree_de'] != '':
            cree_de = datetime.strptime(post['cree_de'], "%d/%m/%Y %H:%M:%S")
            cree_de = datetime.strftime(cree_de, "%Y-%m-%d %H:%M:%S")
            kwargs['date_reception__gte'] = cree_de
        if 'cree_a' in post and post['cree_a'] != '':
            cree_a = datetime.strptime(post['cree_a'], "%d/%m/%Y %H:%M:%S")
            cree_a = datetime.strftime(cree_a, "%Y-%m-%d %H:%M:%S")
            kwargs['date_reception__lte'] = cree_a
        if 'statut' in post and post['statut'] != '':
            kwargs['statut'] = post['statut']
        queryset = self.filter(**kwargs)
        dataset = []
        for row in queryset:
            date_reception = datetime.strftime(row.date_reception, "%d/%m/%Y %H:%M:%S")
            row_list = [date_reception, row.expediteur, row.message, row.get_statut_display(), row.retour]
            dataset.append(row_list)
        return dataset

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
    def filter_for_xls(self, post):
        kwargs = {}
        if 'destinataire' in post and post['destinataire'] != '':
            kwargs['destinataire__icontains'] = str(post['destinataire'])
        if 'message' in post and post['message'] != '':
            kwargs['message__icontains'] = str(post['message'])
        if 'cree_de' in post and post['cree_de'] != '':
            cree_de = datetime.strptime(post['cree_de'], "%d/%m/%Y %H:%M:%S")
            cree_de = datetime.strftime(cree_de, "%Y-%m-%d %H:%M:%S")
            kwargs['date_envoi__gte'] = cree_de
        if 'cree_a' in post and post['cree_a'] != '':
            cree_a = datetime.strptime(post['cree_a'], "%d/%m/%Y %H:%M:%S")
            cree_a = datetime.strftime(cree_a, "%Y-%m-%d %H:%M:%S")
            kwargs['date_envoi__lte'] = cree_a
        queryset = self.filter(**kwargs)
        dataset = []
        for row in queryset:
            date_envoi = datetime.strftime(row.date_envoi, "%d/%m/%Y %H:%M:%S")
            row_list = [date_envoi, row.destinataire, row.message]
            dataset.append(row_list)
        return dataset

class Envoi(Model):
    date_envoi = models.DateTimeField()
    destinataire = models.CharField(max_length=20)
    message = models.CharField(max_length=160)
    ajout = models.DateTimeField(auto_now_add=True)

    objects = EnvoiManager()

    def __unicode__(self):
        return self.nom
# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q, Model, Manager

class BailleurManager(Manager):
    def filter_for_xls(self, post):
        kwargs = {}
        if 'id_nom' in post and post['id_nom'] != '':
            kwargs['nom__icontains'] = str(post['id_nom'])
        if 'id_projet' in post and post['id_projet'] != '':
            kwargs['projet__icontains'] = str(post['id_projet'])
        queryset = self.filter(**kwargs)
        dataset = []
        for row in queryset:
            row_list = [row.nom, row.projet]
            dataset.append(row_list)
        return dataset

class Bailleur(Model):
    nom = models.CharField(max_length=40)
    projet = models.CharField(max_length=200, blank=True, null=True)

    objects = BailleurManager()

    def __unicode__(self):
        return self.nom

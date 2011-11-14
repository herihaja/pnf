# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q, Model, Manager

class BailleurManager(Manager):
    def filter_for_xls(self, post):
        kwargs = {}
        if 'id_nom' in post and post['id_nom'] != '':
            kwargs['nom__icontains'] = str(post['id_nom'])
        queryset = self.filter(**kwargs)
        dataset = []
        for row in queryset:
            row_list = [row.nom]
            dataset.append(row_list)
        return dataset

class Bailleur(Model):
    nom = models.CharField(max_length=40)

    objects = BailleurManager()

    def __unicode__(self):
        return self.nom

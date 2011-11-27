# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q, Model, Manager
from bailleurs.models import Bailleur

class ProjetManager(Manager):
    def filter_for_xls(self, post):
        kwargs = {}
        if 'id_nom' in post and post['id_nom'] != '':
            kwargs['nom__icontains'] = str(post['id_nom'])
        if 'id_bailleurs' in post and post['id_bailleurs'] != '':
            kwargs['bailleurs__in'] = post['id_bailleurs']
        
        queryset = self.filter(**kwargs)
        dataset = []
        for row in queryset:
            bailleurs_list = row.bailleurs.all()
            bailleurs = ''
            if len(bailleurs_list) > 0:
                for bailleur in bailleurs_list:
                    if bailleurs == '':
                        bailleurs = bailleur.nom
                    else:
                        bailleurs = '%s, %s' % (bailleurs, bailleur.nom,)
            row_list = [row.nom, bailleurs]
            dataset.append(row_list)
        return dataset

class Projet(Model):
    nom = models.CharField(max_length=40, unique=True)
    bailleurs = models.ManyToManyField(Bailleur, related_name='projets')

    objects = ProjetManager()

    def __unicode__(self):
        return self.nom

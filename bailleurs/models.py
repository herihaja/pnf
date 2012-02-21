# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Model, Manager

class BailleurManager(Manager):
    def filter_for_xls(self, post):
        kwargs = {}
        if 'id_nom' in post and post['id_nom'] != '':
            kwargs['nom__icontains'] = str(post['id_nom'])
        queryset = self.filter(**kwargs)
        dataset = []
        for row in queryset:
            projets = row.projets.all()
            projets_list = ''
            if len(projets) > 0:
                projets_list = ["%s %s" % (projets_list, projet.nom) for projet in projets]
            if projets_list != '':
                projets_list = ", ".join(projets_list)

            row_list = [row.nom, projets_list]
            dataset.append(row_list)
        return dataset

class Bailleur(Model):
    nom = models.CharField(max_length=40, unique=True)

    objects = BailleurManager()

    def __unicode__(self):
        return self.nom

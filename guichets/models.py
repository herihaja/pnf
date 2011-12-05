# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import models
from django.db.models import Q, Model, Manager
from bailleurs.models import Bailleur
from projets.models import Projet
from localites.models import Commune
from sms.models import Reception

class GuichetManager(Manager):
    def filter_for_xls(self, post):
        kwargs = {}
        if 'commune' in post and post['commune'] != '':
            kwargs['nom__icontains'] = str(post['commune'])
        else:
            if 'code' in post and post['code'] != '':
                kwargs['commune__code__icontains'] = post['code']
            if 'district' in post and post['district'] != '':
                kwargs['commune__district'] = post['district']
            else:
                if 'region' in post and post['region'] != '':
                    kwargs['commune__district__region'] = post['region']
        if 'agf1' in post and post['agf1'] != '':
            kwargs['agf1__icontains'] = str(post['agf1'])
        if 'mobile1' in post and post['mobile1'] != '':
            kwargs['mobile1__icontains'] = str(post['mobile1'])
        if 'agf2' in post and post['agf2'] != '':
            kwargs['agf2__icontains'] = str(post['agf2'])
        if 'mobile2' in post and post['mobile2'] != '':
            kwargs['mobile2__icontains'] = str(post['mobile2'])
        if 'creede' in post and post['creede'] != '':
            cree_de = datetime.strptime(post['creede'], "%d/%m/%Y")
            cree_de = datetime.strftime(cree_de, "%Y-%m-%d")
            kwargs['creation__gte'] = cree_de
        if 'creea' in post and post['creea'] != '':
            cree_a = datetime.strptime(post['creea'], "%d/%m/%Y")
            cree_a = datetime.strftime(cree_a, "%Y-%m-%d")
            kwargs['creation__lte'] = cree_a
        if 'etat' in post and post['etat'] != '':
            kwargs['etat'] = post['etat']
        queryset = self.filter(**kwargs)
        dataset = []
        for row in queryset:
            if row.creation is not None:
                creation = datetime.strftime(row.creation, "%d/%m/%Y")
            else:
                creation = ''
            row_list = [row.commune.nom, row.commune.code, creation, row.agf1,
                        row.mobile1, row.password1, row.agf2, row.mobile2, row.password2, row.get_etat_display()]
            dataset.append(row_list)
        return dataset

    def filter_projets_for_xls(self, post):
        kwargs = {}
        if 'commune' in post and post['commune'] != '':
            kwargs['commune'] = str(post['commune'])
        else:
            if 'code' in post and post['code'] != '':
                kwargs['commune__code__icontains'] = post['code']
            if 'district' in post and post['district'] != '':
                kwargs['commune__district'] = post['district']
            else:
                if 'region' in post and post['region'] != '':
                    kwargs['commune__district__region'] = post['region']
        if 'creede' in post and post['creede'] != '':
            cree_de = datetime.strptime(post['creede'], "%d/%m/%Y")
            cree_de = datetime.strftime(cree_de, "%Y-%m-%d")
            kwargs['creation__gte'] = cree_de
        if 'creea' in post and post['creea'] != '':
            cree_a = datetime.strptime(post['creea'], "%d/%m/%Y")
            cree_a = datetime.strftime(cree_a, "%Y-%m-%d")
            kwargs['creation__lte'] = cree_a
        if 'etat' in post and post['etat'] != '':
            kwargs['etat'] = post['etat']
        if 'projets' in post and post['projets'] != '':
            kwargs['projets__in'] = [int(post['projets'])]
        else:
            if 'bailleurs' in post and post['bailleurs'] != '':
                kwargs['bailleurs__in'] = [int(post['bailleurs'])]

        queryset = self.filter(**kwargs)
        dataset = []
        for row in queryset:
            creation = datetime.strftime(row.creation, "%d/%m/%Y")

            bailleurs_list = row.bailleurs.all()
            bailleurs = ''
            if len(bailleurs_list) > 0:
                for bailleur in bailleurs_list:
                    if bailleurs == '':
                        bailleurs = bailleur.nom
                    else:
                        bailleurs = '%s, %s' % (bailleurs, bailleur.nom,)

            projets_list = row.projets.all()
            projets = ''
            if len(projets_list) > 0:
                for projet in projets_list:
                    if projets == '':
                        projets = projet.nom
                    else:
                        projets = '%s, %s' % (projets, projet.nom,)
            row_list = [row.commune.nom, row.commune.code, creation, bailleurs, projets]
            dataset.append(row_list)
        return dataset

class Guichet(Model):
    CHOIX_ETAT = (
        ('1', 'Ouvert'),
        ('2', 'Suspendu'),
        ('3', 'Fermé'),
        ('4', 'En constitution'),
    )
    commune = models.OneToOneField(Commune, blank=True, null=True, on_delete=models.SET_NULL)
    bailleurs = models.ManyToManyField(Bailleur)
    projets = models.ManyToManyField(Projet)
    creation = models.DateField(blank=True, null=True)
    agf1 = models.CharField(max_length=7, blank=True, null=True)
    mobile1 = models.CharField(max_length=15, blank=True, null=True)
    password1 = models.CharField(max_length=6, blank=True, null=True)
    agf2 = models.CharField(max_length=7, blank=True, null=True)
    mobile2 = models.CharField(max_length=15, blank=True, null=True)
    password2 = models.CharField(max_length=6, blank=True, null=True)
    etat = models.CharField(max_length=1, choices=CHOIX_ETAT)
    ajout = models.DateTimeField(auto_now_add=True)
    edit = models.DateTimeField(auto_now=True)

    objects = GuichetManager()

class Rma(Model):
    guichet = models.ForeignKey(Guichet, on_delete=models.CASCADE)
    sms = models.ForeignKey(Reception, blank=True, null=True, on_delete=models.SET_NULL)
    agf = models.CharField(max_length=7)
    periode = models.DateField()


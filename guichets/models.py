# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q, Model, Manager
from bailleurs.models import Bailleur
from localites.models import Commune

class GuichetManager(Manager):
    def filtrer(self, post):
        qry = Q()

        if 'commune' in post.POST:
            commune = post.POST['commune']
            if len(commune) > 0:
                qry = qry & Q(commune=int(commune))
            else:
                if 'code' in post.POST:
                    code = post.POST['code']
                    if len(code) > 0:
                        qry = qry & Q(commune__code__icontains=code)

                if 'district' in post.POST:
                    district = post.POST['district']
                    if len(district) > 0:
                        qry = qry & Q(commune__district=int(district))
                    else:
                        if 'region' in post.POST:
                            region = post.POST['region']
                            if len(region) > 0:
                                qry = qry & Q(commune__district__region=int(region))

        if 'agf1' in post.POST:
            agf1 = post.POST['agf1']
            if len(agf1) > 0:
                qry = qry & Q(agf1__icontains=agf1)

        if 'mobile1' in post.POST:
            mobile1 = post.POST['mobile1']
            if len(mobile1) > 0:
                qry = qry & Q(mobile1__icontains=mobile1)

        if 'cree_de' in post.POST:
            cree_de = post.POST['cree_de']
            if len(cree_de) > 0:
                qry =  qry & Q(periode__gte=cree_de.strip())

        if 'cree_a' in post.POST:
            cree_a = post.POST['cree_a']
            if len(cree_a) > 0:
                qry =  qry & Q(periode__lte=cree_a.strip())

        if 'etat' in post.POST:
            etat = post.POST['etat']
            if len(etat) > 0:
                qry = qry & Q(etat=etat)

        return self.filter(qry)

class Guichet(Model):
    CHOIX_ETAT = (
        ('1', 'Actif'),
        ('2', 'Non actif'),
        ('3', 'Fermé'),
        ('4', 'En cours'),
    )
    commune = models.ForeignKey(Commune, blank=True, null=True, on_delete=models.SET_NULL)
    bailleur = models.ForeignKey(Bailleur, blank=True, null=True, on_delete=models.SET_NULL)
    creation = models.DateField()
    agf1 = models.CharField(max_length=6, blank=True, null=True)
    mobile1 = models.CharField(max_length=15, blank=True, null=True)
    password1 = models.CharField(max_length=6, blank=True, null=True)
    agf2 = models.CharField(max_length=6, blank=True, null=True)
    mobile2 = models.CharField(max_length=15, blank=True, null=True)
    password2 = models.CharField(max_length=6, blank=True, null=True)
    etat = models.CharField(max_length=1, choices=CHOIX_ETAT)
    ajout = models.DateTimeField(auto_now_add=True)
    edit = models.DateTimeField(auto_now=True)

    objects = GuichetManager()

    def __unicode__(self):
        return self.commune

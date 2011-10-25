# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q, Model, Manager
from localites.models import Commune
from sms.models import Reception

class DonneesManager(Manager):
    def _construire_requete(champ, condition):
        condition = condition.strip()
        if indexOf(condition, '>=') == 0:
            qry = Q({champ + '__gte': int(condition[2:].lstrip())})
            return qry
        if indexOf(condition, '>') == 0:
            qry = Q({champ + '__gt': int(condition[1:].lstrip())})
            return qry
        if indexOf(condition, '<=') == 0:
            qry = Q({champ + '__lte': int(condition[2:].lstrip())})
            return qry
        if indexOf(condition, '<') == 0:
            qry = Q({champ + '__lt': int(condition[1:].lstrip())})
            return qry
        if indexOf(condition, '=') == 0:
            qry = Q(champ=int(condition[1:].lstrip()))
            return qry

    def filtrer(self, post):
        qry = Q()
        indicateurs = ('demandes', 'oppositions', 'resolues', 'certificats', 'femmes', 'recettes', 'mutations', 'surfaces', 'garanties')

        code = post.POST['code']
        commune = post.POST['commune']
        district = post.POST['district']
        region = post.POST['region']
        periode_de_annee = post.POST['periode_de_annee']
        periode_a_annee = post.POST['periode_a_annee']
        periode_de_mois = post.POST['periode_de_mois']
        periode_a_mois = post.POST['periode_a_mois']

        if len(code) > 0:
            qry = qry & Q(commune__code__icontains=code)
        if len(commune) > 0:
            qry = qry & Q(commune=int(commune))
        if len(district) > 0:
            qry = qry & Q(commune__district=int(district))
        if len(region) > 0:
            qry = qry & Q(commune__district__region=int(region))
        for indicateur in indicateurs:
            if len(post.POST[indicateur]) > 0:
                qry = qry & _construire_requete(indicateur, post.POST[indicateur])
        if len(periode_de_annee) > 0:
            if len(periode_de_mois) > 0:
                qry =  qry & Q(periode__gte=periode_de_annee.strip()+'-'+periode_de_mois.strip()+'-01')
            else:
                qry =  qry & Q(periode__gte=periode_de_annee.strip()+'-01-01')
        if len(periode_a_annee) > 0:
            if len(periode_a_mois) > 0:
                qry =  qry & Q(periode__lte=periode_a_annee.strip()+'-'+periode_a_mois.strip()+'-01')
            else:
                qry =  qry & Q(periode__lte=periode_a_annee.strip()+'-01-01')

        return self.filter(qry)

class Donnees(Model):
    commune = models.ForeignKey(Commune, blank=True, null=True, on_delete=models.SET_NULL)
    sms = models.ForeignKey(Reception, blank=True, null=True, on_delete=models.SET_NULL)
    periode = models.DateField()
    demandes = models.IntegerField()
    oppositions = models.IntegerField()
    resolues = models.IntegerField()
    certificats = models.IntegerField()
    femmes = models.IntegerField()
    recettes = models.BigIntegerField()
    mutations = models.IntegerField()
    surfaces = models.FloatField()
    garanties = models.IntegerField()
    reconnaissances = models.IntegerField()
    valide = models.BooleanField(default=False)
    ajout = models.DateTimeField(auto_now_add=True)
    edit = models.DateTimeField(auto_now=True)

    objects = DonneesManager()

    def __unicode__(self):
        return u"données de %s pour %s" % (self.commune.nom, self.periode)

class Cumul(Model):
    commune = models.ForeignKey(Commune, blank=True, null=True, on_delete=models.SET_NULL)
    periode = models.DateField()
    demandes = models.IntegerField()
    oppositions = models.IntegerField()
    resolues = models.IntegerField()
    certificats = models.IntegerField()
    femmes = models.IntegerField()
    recettes = models.BigIntegerField()
    mutations = models.IntegerField()
    surfaces = models.FloatField()
    garanties = models.IntegerField()
    reconnaissances = models.IntegerField()
    ajout = models.DateTimeField(auto_now_add=True)
    edit = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"données de %s pour %s" % (self.commune.nom, self.periode)
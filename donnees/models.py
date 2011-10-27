# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q, Model, Manager
from localites.models import Commune
from sms.models import Reception

class DonneesManager(Manager):
    def _construire_requete(self, champ, condition):
        condition = condition.strip()
        qry = {}
        if condition[0:1] == '>':
            if condition[1:2] == '=':
                qry = {champ + '__gte': int(condition[2:].lstrip())}
            else:
                qry = {champ + '__gt': int(condition[1:].lstrip())}
        if condition[0:1] == '<':
            if condition[1:2] == '=':
                qry = {champ + '__lte': int(condition[2:].lstrip())}
            else:
                qry = {champ + '__lt': int(condition[1:].lstrip())}
        if condition[0:1] == '=' and  (condition[1:2] != '<' or condition[1:2] != '>'):
            qry = {champ: int(condition[1:].lstrip())}
        if len(qry) == 0:
            qry = {champ: int(condition)}
        qry = Q(**qry)
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
                qry =  qry & self._construire_requete(indicateur, post.POST[indicateur])
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

    def __init__(self, *args, **kw):
        ''' Copier les anciennes valeurs pour calculer delta cumul
        '''
        super(Donnees, self).__init__(*args, **kw)
        self._old_demandes = self.demandes
        self._old_oppositions = self.oppositions
        self._old_resolues = self.resolues
        self._old_certificats = self.certificats
        self._old_femmes = self.femmes
        self._old_recettes = self. recettes
        self._old_mutations = self.mutations
        self._old_surfaces = self.surfaces
        self._old_garanties = self.garanties
        self._old_reconnaissances = self.reconnaissances

    def __unicode__(self):
        return u"données de %s pour %s" % (self.commune.nom, self.periode)

    def save(self, *args, **kwargs):
        ''' Calculer delta cumul puis mettre a jour les donnees
        '''
        if self.id is not None:
            delta = {
                'demandes': self.demandes - self._old_demandes,
                'oppositions': self.oppositions - self._old_oppositions,
                'resolues': self.resolues - self._old_resolues,
                'certificats': self.certificats - self._old_certificats,
                'femmes': self.femmes - self._old_femmes,
                'recettes': self. recettes - self._old_recettes,
                'mutations': self.mutations - self._old_mutations,
                'surfaces': self.surfaces - self._old_surfaces,
                'garanties': self.garanties - self._old_garanties,
                'reconnaissances': self.reconnaissances - self._old_reconnaissances
            }
            Cumul.objects.mettre_a_jour(self.commune, self.periode, delta)
            super(Donnees, self).save(*args, **kwargs)
        else:
            super(Donnees, self).save(*args, **kwargs)
            delta = {
                'demandes': self.demandes,
                'oppositions': self.oppositions,
                'resolues': self.resolues,
                'certificats': self.certificats,
                'femmes': self.femmes,
                'recettes': self. recettes,
                'mutations': self.mutations,
                'surfaces': self.surfaces,
                'garanties': self.garanties,
                'reconnaissances': self.reconnaissances
            }
            Cumul.objects.mettre_a_jour(self.commune, self.periode, delta)

    def delete(self, *args, **kwargs):
        ''' Calculer delta cumul puis supprimer les donnees
        '''
        delta = {
            'demandes': -self._old_demandes,
            'oppositions': -self._old_oppositions,
            'resolues': -self._old_resolues,
            'certificats': -self._old_certificats,
            'femmes': -self._old_femmes,
            'recettes': -self._old_recettes,
            'mutations': -self._old_mutations,
            'surfaces': -self._old_surfaces,
            'garanties': -self._old_garanties,
            'reconnaissances': -self._old_reconnaissances
        }
        Cumul.objects.mettre_a_jour(self.commune, self.periode, delta)
        super(Donnees, self).delete(*args, **kwargs)

class CumulManager(Manager):
    def mettre_a_jour(self, commune, periode, delta):
        ''' Ajouter delta a toutes les donnees superieures ou egales a la periode si existe sinon insertion
        '''
        cumuls = self.filter(commune=commune, periode__gte=periode)
        if cumuls is not None:
            for cumul in cumuls:
                obj = Cumul(
                    id = cumul.id,
                    commune = cumul.commune,
                    periode = cumul.periode,
                    demandes = cumul.demandes + delta['demandes'],
                    oppositions = cumul.oppositions + delta['oppositions'],
                    resolues = cumul.resolues + delta['resolues'],
                    certificats = cumul.certificats + delta['certificats'],
                    femmes = cumul.femmes + delta['femmes'],
                    recettes = cumul.recettes + delta['recettes'],
                    mutations = cumul.mutations + delta['mutations'],
                    surfaces = cumul.surfaces + delta['surfaces'],
                    garanties = cumul.garanties + delta['garanties'],
                    reconnaissances = cumul.reconnaissances + delta['reconnaissances'],
                    ajout = cumul.ajout,
                )
                obj.save()
        else:
            obj = Cumul(
                commune = commune,
                periode = periode,
                demandes = delta['demandes'],
                oppositions = delta['oppositions'],
                resolues = delta['resolues'],
                certificats = delta['certificats'],
                femmes = delta['femmes'],
                recettes = delta['recettes'],
                mutations = delta['mutations'],
                surfaces = delta['surfaces'],
                garanties = delta['garanties'],
                reconnaissances = delta['reconnaissances']
            )
            obj.save()

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

    objects = CumulManager()

    def __unicode__(self):
        return u"données de %s pour %s" % (self.commune.nom, self.periode)




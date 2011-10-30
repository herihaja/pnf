# -*- coding: utf-8 -*-
import datetime
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

        if 'periode_de_annee' in post.POST and 'periode_de_mois' in post.POST:
            periode_de_annee = post.POST['periode_de_annee']
            periode_de_mois = post.POST['periode_de_mois']
            if len(periode_de_annee) > 0:
                if len(periode_de_mois) > 0:
                    qry =  qry & Q(periode__gte=periode_de_annee.strip()+'-'+periode_de_mois.strip()+'-01')
                else:
                    qry =  qry & Q(periode__gte=periode_de_annee.strip()+'-01-01')

        if 'periode_a_annee' in post.POST and 'periode_a_mois' in post.POST:
            periode_a_annee = post.POST['periode_a_annee']
            periode_a_mois = post.POST['periode_a_mois']
            if len(periode_a_annee) > 0:
                if len(periode_a_mois) > 0:
                    qry =  qry & Q(periode__lte=periode_a_annee.strip()+'-'+periode_a_mois.strip()+'-01')
                else:
                    qry =  qry & Q(periode__lte=periode_a_annee.strip()+'-12-31')

        if 'annee' in post.POST:
            annee = post.POST['annee']
            if len(annee) > 0:
                qry =  qry & Q(periode__lte=annee.strip()+'-12-31', periode__gte=annee.strip()+'-01-01')

        for indicateur in indicateurs:
            if indicateur in post.POST:
                if len(post.POST[indicateur]) > 0:
                    qry =  qry & self._construire_requete(indicateur, post.POST[indicateur])

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

    class Meta:
        ordering = ['-edit']

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
        self._old_valide = self.valide

    #def __unicode__(self):
    #    return u"données de %s pour %s" % (self.commune.nom, self.periode)

    def save(self, *args, **kwargs):
        ''' Calculer delta puis mettre a jour les cumuls
            Gerer l'activation des donnees, i.e valide
        '''

        if not self._pre_save():
            return False
        
        delta = {'demandes': 0, 'oppositions': 0, 'resolues': 0, 'certificats': 0, 'femmes': 0, 'recettes': 0,
                 'mutations': 0, 'surfaces': 0, 'garanties': 0, 'reconnaissances': 0,}
        if self.valide == True:
            # Si nouvelles donnees validees
            if self.id is not None and self._old_valide == True:
                # Si anciennes valeurs existent
                delta['demandes'] -= self._old_demandes
                delta['oppositions'] -= self._old_oppositions
                delta['resolues'] -= self._old_resolues
                delta['certificats'] -= self._old_certificats
                delta['femmes'] -= self._old_femmes
                delta['recettes'] -= self._old_recettes
                delta['mutations'] -= self._old_mutations
                delta['surfaces'] -= self._old_surfaces
                delta['garanties'] -= self._old_garanties
                delta['reconnaissances'] -= self._old_reconnaissances
            else:
                # Rechercher si il y des anciennes donnees validees
                valide = Donnees.objects.filter(commune=self.commune, periode=self.periode, valide=True)
                # on retire les chiffres des cumuls
                if len(valide) == 1:
                    valide = valide[0]
                    delta['demandes'] -= valide.demandes
                    delta['oppositions'] -= valide.oppositions
                    delta['resolues'] -= valide.resolues
                    delta['certificats'] -= valide.certificats
                    delta['femmes'] -= valide.femmes
                    delta['recettes'] -= valide.recettes
                    delta['mutations'] -= valide.mutations
                    delta['surfaces'] -= valide.surfaces
                    delta['garanties'] -= valide.garanties
                    delta['reconnaissances'] -= valide.reconnaissances
                    Donnees.objects.filter(pk=valide.id).update(valide=False)

            # on enregistre les nouvelles donnees
            super(Donnees, self).save(*args, **kwargs)
            # on rajoute les nouveaux chiffres
            delta['demandes'] += self.demandes
            delta['oppositions'] += self.oppositions
            delta['resolues'] += self.resolues
            delta['certificats'] += self.certificats
            delta['femmes'] += self.femmes
            delta['recettes'] += self.recettes
            delta['mutations'] += self.mutations
            delta['surfaces'] += self.surfaces
            delta['garanties'] += self.garanties
            delta['reconnaissances'] += self.reconnaissances
            Cumul.objects.mettre_a_jour(self.commune, self.periode, delta)
        else:
            if self.id is not None and self._old_valide == True:
                # Si anciennes valeurs existent
                delta['demandes'] -= self._old_demandes
                delta['oppositions'] -= self._old_oppositions
                delta['resolues'] -= self._old_resolues
                delta['certificats'] -= self._old_certificats
                delta['femmes'] -= self._old_femmes
                delta['recettes'] -= self._old_recettes
                delta['mutations'] -= self._old_mutations
                delta['surfaces'] -= self._old_surfaces
                delta['garanties'] -= self._old_garanties
                delta['reconnaissances'] -= self._old_reconnaissances
                Cumul.objects.mettre_a_jour(self.commune, self.periode, delta)
            super(Donnees, self).save(*args, **kwargs)

        return True

    def delete(self, *args, **kwargs):
        ''' Calculer delta cumul puis supprimer les donnees
        '''

        if not self._pre_delete():
            return False

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
        super(Donnees, self).delete(*args, **kwargs)
        Cumul.objects.mettre_a_jour(self.commune, self.periode, delta)

        return True

    def _pre_save(self):
        ''' Verifier qu'il n'y a pas de blancs entre 2 periodes
        '''
        dernier = Donnees.objects.filter(commune=self.commune).order_by("-periode")[:1]
        if len(dernier) == 1:
            derniere_periode = datetime.datetime.combine(dernier[0].periode, datetime.time())
            if isinstance(self.periode, basestring):
                periode = datetime.datetime.strptime(self.periode, "%Y-%m-%d")
            else:
                periode = datetime.datetime.combine(self.periode, datetime.time())
            delta = periode - derniere_periode
            delta = delta.days
            if delta > 31:
                return False
        return True

    def _pre_delete(self):
        ''' Verifier qu'il n'y a pas de donnees après la periode a supprimer
        '''
        suivant = Donnees.objects.filter(commune=self.commune, periode__gt=periode)
        if len(suivant) > 0:
            return False
        return True
            

class CumulManager(Manager):
    def mettre_a_jour(self, commune, periode, delta):
        ''' Ajouter delta a toutes les donnees superieures ou egales a la periode si existe sinon insertion
        '''
        cumuls = self.filter(commune=commune, periode__gte=periode)
        if len(cumuls):
            for cumul in cumuls:
                Cumul.objects.filter(pk=cumul.id).update(
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
                )
        else:
            ''' Rechercher le dernier enregistrement et s'en servir comme base
            '''
            depart = {'demandes': 0, 'oppositions': 0, 'resolues': 0, 'certificats': 0, 'femmes': 0, 'recettes': 0,
                 'mutations': 0, 'surfaces': 0, 'garanties': 0, 'reconnaissances': 0,}
            precedent = Cumul.objects.filter(commune=commune).order_by("-periode")[:1]
            if len(precedent) > 0:
                precedent = precedent[0]
                depart['demandes'] += precedent.demandes
                depart['oppositions'] += precedent.oppositions
                depart['resolues'] += precedent.resolues
                depart['certificats'] += precedent.certificats
                depart['femmes'] += precedent.femmes
                depart['recettes'] += precedent.recettes
                depart['mutations'] += precedent.mutations
                depart['surfaces'] += precedent.surfaces
                depart['garanties'] += precedent.garanties
                depart['reconnaissances'] += precedent.reconnaissances

            obj = Cumul(
                commune = commune,
                periode = periode,
                demandes = delta['demandes'] + depart['demandes'],
                oppositions = delta['oppositions'] + depart['oppositions'],
                resolues = delta['resolues'] + depart['resolues'],
                certificats = delta['certificats'] + depart['certificats'],
                femmes = delta['femmes'] + depart['femmes'],
                recettes = delta['recettes'] + depart['recettes'],
                mutations = delta['mutations'] + depart['mutations'],
                surfaces = delta['surfaces'] + depart['surfaces'],
                garanties = delta['garanties'] + depart['garanties'],
                reconnaissances = delta['reconnaissances'] + depart['reconnaissances']
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
    filtered_objects = DonneesManager()

    def __unicode__(self):
        return u"données de %s pour %s" % (self.commune.nom, self.periode)

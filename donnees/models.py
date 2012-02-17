# -*- coding: utf-8 -*-
from __future__ import division
from datetime import datetime
from django.db import models
from django.db.models import Q, Model, Manager
from guichets.models import Guichet
from helpers import create_compare_condition
from localites.models import Commune
from sms.models import Reception
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist

class DonneesManager(Manager):
    def filter_for_xls(self, post):
        columns = ['demandes', 'oppositions', 'resolues', 'certificats', 'femmes', 'surfaces', 'recettes', 'garanties', 'reconnaissances', 'mutations']
        kwargs = {'valide': True}
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

        for i in range(0, 9):
            post_key = columns[i]
            if post_key in post and post[post_key] != '':
                key, value = create_compare_condition(columns[i], post[post_key])
                kwargs[key] = value

        if 'date_de' in post and post['date_de'] != '':
            cree_de = datetime.strptime(post['date_de'], "%d/%m/%Y")
            cree_de = datetime.strftime(cree_de, "%Y-%m-%d")
            kwargs['periode__gte'] = cree_de
        if 'date_a' in post and post['date_a'] != '':
            cree_a = datetime.strptime(post['date_a'], "%d/%m/%Y")
            cree_a = datetime.strftime(cree_a, "%Y-%m-%d")
            kwargs['periode__lte'] = cree_a

        if 'recu_de' in post and post['recu_de'] != '':
            recu_de = datetime.strptime(post['recu_de'], "%d/%m/%Y")
            recu_de = datetime.strftime(recu_de, "%Y-%m-%d")
            kwargs['reception__gte'] = recu_de
        if 'recu_a' in post and post['recu_a'] != '':
            recu_a = datetime.strptime(post['recu_a'], "%d/%m/%Y")
            recu_a = datetime.strftime(recu_a, "%Y-%m-%d")
            kwargs['reception__lte'] = cree_a
        
        queryset = self.filter(**kwargs)
        dataset = []
        for row in queryset:
            periode = datetime.strftime(row.periode, "%m/%Y")
            row_list = [row.commune.nom, row.commune.code, periode, row.demandes, row.oppositions, row.resolues,
                        row.certificats, row.femmes, row.surfaces, row.recettes, row.garanties, row.reconnaissances, row.mutations]
            dataset.append(row_list)
        return dataset

    def filter_for_site(self, post):
        columns = ['demandes', 'oppositions', 'resolues', 'certificats', 'femmes', 'surfaces', 'recettes', 'garanties', 'reconnaissances', 'mutations']
        kwargs = {'valide': True}
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

        for i in range(0, 9):
            post_key = columns[i]
            if post_key in post and post[post_key] != '':
                key, value = create_compare_condition(columns[i], post[post_key])
                kwargs[key] = value

        if 'date_de' in post and post['date_de'] != '':
            cree_de = datetime.strptime(post['date_de'], "%d/%m/%Y")
            cree_de = datetime.strftime(cree_de, "%Y-%m-%d")
            kwargs['periode__gte'] = cree_de
        if 'date_a' in post and post['date_a'] != '':
            cree_a = datetime.strptime(post['date_a'], "%d/%m/%Y")
            cree_a = datetime.strftime(cree_a, "%Y-%m-%d")
            kwargs['periode__lte'] = cree_a

        queryset = self.filter(**kwargs)
        dataset = []
        for row in queryset:
            annee = datetime.strftime(row.periode, "%Y")
            mois = datetime.strftime(row.periode, "%m")
            columns = [u'ID_COMMUNE', u'ANNEE', u'MOIS', u'REGION', u'DISTRICT', u'COMMUNES', u'BAILLEUR',
               u'NB_DEMANDE', u'NB_DEM_REJ', u'NB_CF_DELI', u'NB_CF_FEMM', u'NB_BENEFIC', u'NB_BENEF_F',
               u'SUPERFICIE', u'NB_OPPOSIT', u'NB_OPP_RES', u'RECETTE']

            bailleurs = ''
            try:
                guichet = row.commune.guichet
                bailleurs_list = guichet.bailleurs.all()
                if len(bailleurs_list) > 0:
                    for bailleur in bailleurs_list:
                        if bailleurs == '':
                            bailleurs = bailleur.nom
                        else:
                            bailleurs = '%s, %s' % (bailleurs, bailleur.nom,)
            except ObjectDoesNotExist:
                pass

            row_list = [row.commune.code, annee, mois, row.commune.district.region.nom, row.commune.district.nom, row.commune.nom,
                        bailleurs, row.demandes, '', row.certificats, row.femmes, '', '', row.surfaces, row.oppositions, row.resolues,
                        row.recettes]
            dataset.append(row_list)
        return dataset

    def filter_ratio_for_xls(self, post):
        kwargs = {}
        # indicateur valide is mandatory
        if 'indicateur' in post and  post['indicateur'] != '':
            indicateur = str(post['indicateur'])
        # year is mandatory
        if 'annee' in post and  post['annee'] != '':
            year = str(post['annee'])
        else:
            year = datetime.now().year - 1
        kwargs['periode__year'] = year

        if 'commune' in post and post['commune'] != '':
            kwargs['commune'] = str(post['commune'])
        else:
            if 'code' in post and post['code'] != '':
                kwargs['code__icontains'] = post['code']
            if 'district' in post and post['district'] != '':
                kwargs['commune__district'] = post['district']
            else:
                if 'region' in post and post['region'] != '':
                    kwargs['commune__district__region'] = post['region']

        cumuls = Cumul.objects.filter(**kwargs).values('commune', 'commune__nom').annotate(Count('commune'))
        results = []
        for cumul in cumuls:
            ratios = Cumul.objects.filter(periode__year=year, commune=cumul['commune']).values('periode', indicateur).order_by('periode')
            nom = cumul['commune__nom']
            ratio = {}
            total = 0
            n = 0
            m = 1
            for row in ratios:
                month = row['periode'].month
                # fill the blanks
                while month > m:
                    ratio[str(m)] = '-'
                    m += 1
                if row[indicateur] is not None:
                    ratio[str(m)] = row[indicateur]
                    total += row[indicateur]
                else:
                    ratio[str(m)] = '-'
                n += 1
                m += 1
            # fill the blanks
            while m <= 12:
                ratio[str(m)] = '-'
                m += 1
            moyenne = round(total / n, 2)
            total = total
            row_list = [nom, ratio['1'], ratio['2'], ratio['3'], ratio['4'], ratio['5'],
                        ratio['6'], ratio['7'], ratio['8'], ratio['9'], ratio['10'], ratio['11'], ratio['12'], moyenne, total]
            results.append(row_list)
        return results


class Donnees(Model):
    commune = models.ForeignKey(Commune, blank=True, null=True, on_delete=models.SET_NULL)
    sms = models.ForeignKey(Reception, blank=True, null=True, on_delete=models.SET_NULL)
    periode = models.DateField()
    reception = models.DateTimeField()
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

    def __init__(self, *args, **kwargs):
        """ Copier les anciennes valeurs pour calculer delta cumul
        """
        super(Donnees, self).__init__(*args, **kwargs)
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

    def __unicode__(self):
        return u"données de %s pour %s" % (self.commune.nom, self.periode)

    def save(self, *args, **kwargs):
        """ Calculer delta puis mettre a jour les cumuls
            Gerer l'activation des donnees, i.e valide
        """
        
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
        """ Calculer delta cumul puis supprimer les donnees
        """
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
        """ Verifier qu'il n'y a pas de blancs entre 2 periodes
        """
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
        """ Verifier qu'il n'y a pas de donnees après la periode a supprimer
        """
        suivant = Donnees.objects.filter(commune=self.commune, periode__gt=periode)
        if len(suivant) > 0:
            return False
        return True
            

class CumulManager(Manager):
    def filter_for_xls(self, post):
        columns = ['demandes', 'oppositions', 'resolues', 'certificats', 'femmes', 'surfaces', 'recettes', 'garanties', 'reconnaissances', 'mutations']
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

        for i in range(0, 9):
            post_key = columns[i]
            if post_key in post and post[post_key] != '':
                key, value = create_compare_condition(columns[i], post[post_key])
                kwargs[key] = value

        if 'periode_de' in post and post['periode_de'] != '':
            cree_de = datetime.strptime(post['periode_de'], "%d/%m/%Y")
            cree_de = datetime.strftime(cree_de, "%Y-%m-%d")
            kwargs['periode__gte'] = cree_de
        if 'periode_a' in post and post['periode_a'] != '':
            cree_a = datetime.strptime(post['periode_a'], "%d/%m/%Y")
            cree_a = datetime.strftime(cree_a, "%Y-%m-%d")
            kwargs['periode__lte'] = cree_a

        queryset = self.filter(**kwargs)
        dataset = []
        for row in queryset:
            periode = datetime.strftime(row.periode, "%m/%Y")
            row_list = [row.commune.nom, row.commune.code, periode, row.demandes, row.oppositions, row.resolues,
                        row.certificats, row.femmes, row.recettes, row.mutations, row.surfaces, row.garanties, row.reconnaissances]
            dataset.append(row_list)
        return dataset

    def _calcul_ratio(self, demandes, certificats, femmes, oppositions, resolues, surfaces):
        if demandes is not None and demandes != 0:
            rcertificats = round(certificats / demandes, 2)
            rconflits = round(oppositions / demandes, 2)
        else:
            rcertificats = None
            rconflits = None

        if certificats is not None and certificats != 0:
            rfemmes = round(femmes / certificats, 2)
            rsurface = round(surfaces /  certificats, 2)
        else:
            rfemmes = None
            rsurface = None

        if oppositions is not None and oppositions != 0:
            rresolus = round(resolues / oppositions, 2)
        else:
            rresolus = None

        return rcertificats, rfemmes, rresolus, rconflits, rsurface
        
    def mettre_a_jour(self, commune, periode, delta):
        """ Ajouter delta a toutes les donnees superieures ou egales a la periode si existe sinon insertion
        """
        cumuls = self.filter(commune=commune, periode__gte=periode)
        if len(cumuls):
            for cumul in cumuls:
                demandes = cumul.demandes + delta['demandes']
                oppositions = cumul.oppositions + delta['oppositions']
                resolues = cumul.resolues + delta['resolues']
                certificats = cumul.certificats + delta['certificats']
                femmes = cumul.femmes + delta['femmes']
                recettes = cumul.recettes + delta['recettes']
                mutations = cumul.mutations + delta['mutations']
                surfaces = cumul.surfaces + delta['surfaces']
                garanties = cumul.garanties + delta['garanties']
                reconnaissances = cumul.reconnaissances + delta['reconnaissances']
                rcertificats, rfemmes, rresolus, rconflits, rsurface = \
                self._calcul_ratio(demandes, certificats, femmes, oppositions, resolues, surfaces)

                obj = Cumul(
                    id = cumul.id,
                    commune = cumul.commune,
                    periode = cumul.periode,
                    demandes = demandes,
                    oppositions = oppositions,
                    resolues = resolues,
                    certificats = certificats,
                    femmes = femmes,
                    recettes = recettes,
                    mutations = mutations,
                    surfaces = surfaces,
                    garanties = garanties,
                    reconnaissances = reconnaissances,
                    rcertificats = rcertificats,
                    rfemmes = rfemmes,
                    rresolus = rresolus,
                    rconflits = rconflits,
                    rsurface = rsurface,
                    ajout = cumul.ajout
                )
                obj.save()
        else:
            """ Rechercher le dernier enregistrement et s'en servir comme base
            """
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

            demandes = delta['demandes'] + depart['demandes']
            oppositions = delta['oppositions'] + depart['oppositions']
            resolues = delta['resolues'] + depart['resolues']
            certificats = delta['certificats'] + depart['certificats']
            femmes = delta['femmes'] + depart['femmes']
            recettes = delta['recettes'] + depart['recettes']
            mutations = delta['mutations'] + depart['mutations']
            surfaces = delta['surfaces'] + depart['surfaces']
            garanties = delta['garanties'] + depart['garanties']
            reconnaissances = delta['reconnaissances'] + depart['reconnaissances']
            rcertificats, rfemmes, rresolus, rconflits, rsurface = \
                self._calcul_ratio(demandes, certificats, femmes, oppositions, resolues, surfaces)
            obj = Cumul(
                commune = commune,
                periode = periode,
                demandes = demandes,
                oppositions = oppositions,
                resolues = resolues,
                certificats = certificats,
                femmes = femmes,
                recettes = recettes,
                mutations = mutations,
                surfaces = surfaces,
                garanties = garanties,
                reconnaissances = reconnaissances,
                rcertificats = rcertificats,
                rfemmes = rfemmes,
                rresolus = rresolus,
                rconflits = rconflits,
                rsurface = rsurface
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
    rcertificats = models.FloatField(blank=True, null=True)
    rfemmes = models.FloatField(blank=True, null=True)
    rconflits = models.FloatField(blank=True, null=True)
    rresolus = models.FloatField(blank=True, null=True)
    rsurface = models.FloatField(blank=True, null=True)
    ajout = models.DateTimeField(auto_now_add=True)
    edit = models.DateTimeField(auto_now=True)

    objects = CumulManager()
    filtered_objects = DonneesManager()

    def __unicode__(self):
        return u"données de %s pour %s" % (self.commune.nom, self.periode)


class RecuManager(Manager):
    def filter_for_xls(self, post, rejete=None):
        # columns = ['demandes', 'oppositions', 'resolues', 'certificats', 'femmes', 'surfaces', 'recettes', 'garanties', 'reconnaissances', 'mutations']
        kwargs = {'rejete': rejete}
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

        queryset = self.filter(**kwargs)
        dataset = []
        for row in queryset:
            periode = datetime.strftime(row.periode, "%m/%Y")
            row_list = [row.commune.nom, row.commune.code, periode, row.demandes, row.oppositions, row.resolues,
                        row.certificats, row.femmes, row.surfaces, row.recettes, row.garanties, row.reconnaissances, row.mutations]
            dataset.append(row_list)
        return dataset

    
class Recu(Model):
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
    rejete = models.BooleanField(default=False)
    ajout = models.DateTimeField(auto_now_add=True)
    doublon = models.BooleanField(default=False)

    def __unicode__(self):
        return self.id

    objects = RecuManager()

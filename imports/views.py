# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from bailleurs.models import Bailleur
from donnees.models import Donnees
from guichets.models import Guichet
from localites.models import Province, Region, Commune, District
import xlrd
from projets.models import Projet
from django.views.decorators.csrf import csrf_view_exempt
import settings

LISTE_MOIS = {
    'janvier' : '01',
    'fevrier' : '02',
    'mars' : '03',
    'avril' : '04',
    'mai' : '05',
    'juin' : '06',
    'juillet' : '07',
    'aout' : '08',
    'septembre' : '09',
    'octobre' : '10',
    'novembre' : '11',
    'decembre' : '12'
}

def _nettoyer_nom(nom, code):
    nom = nom.strip()
    nom = nom.replace('  ', '')
    slug = slugify(nom)
    code = str(int(code))
    return nom, slug, code

def _convesion_int(n):
    if n is None or n == '':
        n = 0
    else:
        n = int(n)
    return n

def _convesion_float(n):
    if n is None or n == '':
        n = 0
    else:
        n = float(n)
    return n

def _ajouter_province(nom, code):
    nom, slug, code = _nettoyer_nom(nom, code)
    obj, created = Province.objects.get_or_create(slug=slug, code=code, nom=nom)
    return obj

def _ajouter_region(nom, code, province):
    nom, slug, code = _nettoyer_nom(nom, code)
    obj, created = Region.objects.get_or_create(slug=slug, code=code, nom=nom, province=province)
    return obj

def _ajouter_district(nom, code, region):
    nom, slug, code = _nettoyer_nom(nom, code)
    obj, created = District.objects.get_or_create(slug=slug, code=code, nom=nom, region=region)
    return obj

def _ajouter_commune(nom, code, district):
    nom, slug, code = _nettoyer_nom(nom, code)
    obj, created = Commune.objects.get_or_create(slug=slug, code=code, nom=nom, district=district)
    return obj, created

@csrf_view_exempt
def importer_data(request):
    if request.method == "GET":
        return render_to_response("imports/import.html")
    f = request.FILES['donnees']
    filename = settings.MEDIA_ROOT+'/data.xls'
    destination = open(filename, 'wb+')

    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    
    book = xlrd.open_workbook(filename)
    
    sheet = book.sheets()[0]

    data_ignored = []
    data_added = 0
    
    for i in xrange(sheet.nrows):
        row = sheet.row_values(i)
        nom, slug, code =  _nettoyer_nom(row[5], row[1])
        try:
            commune = Commune.objects.get(slug=slug, code=code, nom=nom)
            annee = row[2]
            mois = row[6]
            if annee is not None and annee != '' and mois is not None and mois != '':
                mois = mois.strip()
                mois = slugify(mois)
                annee = str(int(annee))
                
                if mois in LISTE_MOIS:
                    mois = LISTE_MOIS[mois]
                    periode = annee + '-' + mois + '-01'
                    obj = Donnees(
                        commune = commune,
                        periode = periode,
                        demandes = _convesion_int(row[7]),
                        oppositions = _convesion_int(row[8]),
                        resolues = _convesion_int(row[9]),
                        certificats = _convesion_int(row[10]),
                        femmes = _convesion_int(row[11]),
                        surfaces = _convesion_float(row[12]),
                        recettes = _convesion_float(row[13]),
                        garanties = _convesion_int(row[14]),
                        reconnaissances = _convesion_int(row[15]),
                        mutations = _convesion_int(row[16]),
                        valide = True,
                    )
                    if obj.save():
                        data_added += 1
                    else:
                        data_ignored.append(u'Mois pr??c??dents non remplis ligne %s' % i)
                else:
                    data_ignored.append('Mois introuvable ligne %s' % i)
            else:
                data_ignored.append('Annee ou mois vide ligne' % i)
        except Commune.DoesNotExist:
            data_ignored.append('Commune introuvable ligne %s' % i)
    import os
    os.remove(filename)
    return render_to_response('imports/importer_donnees.html', {"data_ignored": data_ignored, "data_added": data_added},
                              context_instance=RequestContext(request))

@login_required(login_url="/connexion")
def importer_donnees(request):
    book = xlrd.open_workbook("media/data2010.xls")
    sheet = book.sheets()[0]

    data_ignored = []
    data_added = 0
    for i in xrange(sheet.nrows):
        row = sheet.row_values(i)
        nom, slug, code =  _nettoyer_nom(row[5], row[1])
        try:
            commune = Commune.objects.get(slug=slug, code=code, nom=nom)
            annee = row[2]
            mois = row[6]
            if annee is not None and annee != '' and mois is not None and mois != '':
                mois = mois.strip()
                mois = slugify(mois)
                annee = str(int(annee))
                
                if mois in LISTE_MOIS:
                    mois = LISTE_MOIS[mois]
                    periode = annee + '-' + mois + '-01'
                    obj = Donnees(
                        commune = commune,
                        periode = periode,
                        demandes = _convesion_int(row[7]),
                        oppositions = _convesion_int(row[8]),
                        resolues = _convesion_int(row[9]),
                        certificats = _convesion_int(row[10]),
                        femmes = _convesion_int(row[11]),
                        surfaces = _convesion_float(row[12]),
                        recettes = _convesion_float(row[13]),
                        garanties = _convesion_int(row[14]),
                        reconnaissances = _convesion_int(row[15]),
                        mutations = _convesion_int(row[16]),
                        valide = True,
                    )
                    if obj.save():
                        data_added += 1
                    else:
                        data_ignored.append(u'Mois pr??c??dents non remplis ligne %s' % i)
                else:
                    data_ignored.append('Mois introuvable ligne %s' % i)
            else:
                data_ignored.append('Annee ou mois vide ligne' % i)
        except Commune.DoesNotExist:
            data_ignored.append('Commune introuvable ligne %s' % i)

    return render_to_response('imports/importer_donnees.html', {"data_ignored": data_ignored, "data_added": data_added},
                              context_instance=RequestContext(request))

@login_required(login_url="/connexion")
def importer_localites(request):
    book = xlrd.open_workbook("media/localites.xls")
    sheet = book.sheets()[0]

    data_ignored = []
    data_added = 0
    for i in xrange(sheet.nrows):
        row = sheet.row_values(i)
        if row[2] != '' and row[3] != '':
            province = _ajouter_province(row[2], row[3])
            if row[4] != '' and row[5] != '':
                region = _ajouter_region(row[4], row[5], province)
                if row[6] != '' and row[7] != '':
                    district = _ajouter_district(row[6], row[7], region)
                    if row[1] != '' and row[0] != '':
                        _ajouter_commune(row[1], row[0], district)
                        data_added += 1
                    else:
                        data_ignored.append('%s commune manquante' %(i,))
                else:
                    data_ignored.append('%s district manquant' %(i,))
            else:
                data_ignored.append('%s region manquante' %(i,))
        else:
            data_ignored.append('%s province manquante' %(i,))
    return render_to_response('imports/importer_donnees.html', {"data_ignored": data_ignored, "data_added": data_added},
                              context_instance=RequestContext(request))

@login_required(login_url="/connexion")
def importer_bailleurs(request):
    STATUT = ['1', '2', '3', '4']
    book = xlrd.open_workbook("media/bailleurs.xls")
    sheet = book.sheets()[0]

    data_ignored = []
    data_added = 0
    for i in xrange(sheet.nrows):
        commune = None

        row = sheet.row_values(i)
        # retrouver la commune
        if row[2] != '':
            slug = row[2].strip()
            slug = slugify(slug)
        communes = Commune.objects.filter(slug=slug)
        if len(communes) == 0:
            data_ignored.append('%s commune inconnue' %(i,))
        elif len(communes) > 1:
            # rechercher district
            slug_district = row[1].strip()
            slug_district = slugify(slug_district)
            n = 0
            for c in communes:
                if c.district.slug == slug_district:
                    commune = c
                    n += 1
            if n == 0:
                data_ignored.append('%s commune inconnue' %(i,))
            elif n == 2:
                commune = Nonerequest
                data_ignored.append('%s commune ambig??e' %(i,))
        else:
            commune = communes[0]
            #v??rifier doublon
            obj = Guichet.objects.filter(commune__id=commune.id)
            if len(obj) > 0:
                commune = None
                data_ignored.append('%s guichet en doublon' %(i,))

        if commune is not None:
            # retrouver bailleur
            nom = row[3].strip()
            nom = nom.split('/')
            bailleurs = []
            projets = []
            for n in nom:
                bailleur  = Bailleur.objects.filter(nom=n)
                if len(bailleur) == 1:
                    bailleurs.append(bailleur[0])
                projet = Projet.objects.filter(nom=n)
                if len(projet) == 1:
                    projets.append(projet[0])
            # retrouver le statut
            statut = str(int(row[4]))
            if statut in STATUT:
                if statut != '4':
                    # date ouverture
                    if row[5] != '' and row[6] != '':
                        creation = datetime(int(row[5]), int(row[6]), 1)
                        creation = datetime.strftime(creation, '%Y-%m-%d')

                    guichet = Guichet(
                            commune = commune,
                            creation = creation,
                            etat = statut,
                        )

                    # code AGF1
                    if row[7] != '':
                        agf1 = row[7].strip()
                        guichet.agf1=agf1
                        if row[8] != '':
                            password1 = row[8]
                            guichet.password1=password1
                    # code AGF2
                    if row[9] != '':
                        agf2 = row[9].strip()
                        guichet.agf2=agf2
                        if row[10] != '':
                            password2 = row[10]
                            guichet.password2=password2
                else:
                    guichet = Guichet(
                        commune = commune,
                        etat = statut,
                    )
                guichet.save()
                for bailleur in bailleurs:
                    guichet.bailleurs.add(bailleur)
                for projet in projets:
                    guichet.projets.add(projet)
                data_added += 1
            else:
                data_ignored.append('%s statut inconnu' % (i,))
    return render_to_response('imports/importer_donnees.html', {"data_ignored": data_ignored, "data_added": data_added},
                              context_instance=RequestContext(request))
            

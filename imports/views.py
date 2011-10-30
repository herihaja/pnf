# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from donnees.models import Donnees
from localites.views import Commune, District
from datetime import date
import xlrd

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

def _nettoyer_nom(nom):
    nom = nom.strip()
    nom = nom.replace('  ', '')
    nom = slugify(nom)
    return nom

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

def _ajouter_commune(commune, code, district):
    commune_slug =  _nettoyer_nom(commune)
    commune_code = str(int(code))
    district_slug = _nettoyer_nom(district)
    try:
        commune_obj = Commune.objects.get(slug=commune_slug, district__slug=district_slug)
    except Commune.DoesNotExist:
        try:
            district_obj = District.objects.get(slug=district_slug)
            commune_obj = Commune(nom=commune, code=commune_code, slug=commune_slug, district=district_obj)
            commune_obj.save()
        except District.DoesNotExist:
            return None

    return commune_obj

def importer_donnees(request):
    book = xlrd.open_workbook("media/data2010.xls")
    sheet = book.sheets()[0]

    data_ignored = []
    data_added = 0
    for i in xrange(sheet.nrows):
        row = sheet.row_values(i)
        commune = _ajouter_commune(row[5], row[1], row[4])
        if commune is not None:
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
                        data_ignored.append(u'Mois précédents non remplis ligne %s' % i)
                else:
                    data_ignored.append('Mois introuvable ligne %s' % i)
            else:
                data_ignored.append('Annee ou mois vide ligne' % i)
        else:
            data_ignored.append('Commune introuvable ligne %s' % i)

    return render_to_response('imports/importer_donnees.html', {"data_ignored": data_ignored, "data_added": data_added},
                              context_instance=RequestContext(request))
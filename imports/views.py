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

def _ajouter_commune(commune, code, district):
    commune_nom = commune.strip()
    commune_nom = commune_nom.replace('  ', '')
    commune_code = str(int(code))
    try:
        commune_obj = Commune.objects.get(nom__iexact=commune_nom)
    except Commune.DoesNotExist:
        try:
            district_nom = district.strip()
            district_nom = district_nom.replace('  ', '')
            district_obj = District.objects.get(nom__iexact=district_nom)
            commune_obj = Commune(nom=commune, code=commune_code, district=district_obj)
            commune_obj.save()
        except District.DoesNotExist:
            return None

    return commune_obj

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

def importer_donnees(request):
    book = xlrd.open_workbook("media/data2010.xls")
    sheet = book.sheets()[0]

    data_ignored = []
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

                    # verifier si doublon
                    doublon = Donnees.objects.filter(periode=periode, commune=commune, valide=True)
                    if doublon is not None:
                        valide = False
                    else:
                        valide = True

                    # insertion donnee
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
                        valide = valide
                    )
                    obj.save()
                    print obj
                else:
                    data_ignored.append('%s mois' % i)
            else:
                data_ignored.append('%s annee / mois' % i)
        else:
            data_ignored.append('%s commune' % i)

    return render_to_response('imports/importer_donnees.html', {"data_ignored": data_ignored},
                              context_instance=RequestContext(request))
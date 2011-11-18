# -*- coding: utf-8 -*-
from __future__ import division
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from donnees.models import Donnees, Cumul
from donnees.views import editer_donnees, supprimer_donnees
from helpers import process_datatables_posted_vars, query_datatables, export_excel
from indicateurs.forms import FiltreIndicateursForm, FiltreIndicateurForm, FiltreRatioForm
from django.db.models import Count
import simplejson
from datetime import datetime
from localites.models import District, Commune

def indicateurs_par_date(request):
    if request.method == 'GET':
        form = FiltreIndicateursForm()
    else:
        form = FiltreIndicateursForm(request.POST)
    page_js = '/media/js/indicateurs/indicateurs.js'
    title = 'Indicateurs par localités'
    return render_to_response('layout_list.html', {"form": form, "title": title, "page_js": page_js},
                              context_instance=RequestContext(request))

def indicateur_par_date(request):
    if request.method == 'GET':
        form = FiltreIndicateurForm(initial={'annee': datetime.now().year - 1})
    else:
        form = FiltreIndicateurForm(request.POST)
    title = 'Indicateur par année'
    page_js = '/media/js/indicateurs/ratios.js'
    return render_to_response('layout_list.html', {"form": form, "title": title, "page_js": page_js},
                              context_instance=RequestContext(request))

def ratio(request, ratio, title):
    if request.method == 'GET':
        form = FiltreRatioForm(initial={'indicateur': ratio, 'annee': datetime.now().year - 1})
    else:
        form = FiltreRatioForm(request.POST)
    page_js = '/media/js/indicateurs/ratios.js'
    return render_to_response('layout_ratio_list.html', {"form": form, "title": title, "page_js": page_js},
                              context_instance=RequestContext(request))

def ajax_indicateurs(request):
    # columns titles
    columns = ['commune', 'code', 'periode', 'demandes', 'oppositions', 'resolues', 'certificats', 'femmes', 'surfaces', 'recettes', 'garanties', 'reconnaissances', 'mutations', 'actions']

    # filtering
    post = process_datatables_posted_vars(request.POST)
    # valide true
    kwargs = {'valide': True}
    if 'fCommune' in post and post['fCommune'] != '':
        kwargs['nom__icontains'] = str(post['fCommune'])
    else:
        if 'fCode' in post and post['fCode'] != '':
            kwargs['commune__code__icontains'] = post['fCode']
        if 'fDistrict' in post and post['fDistrict'] != '':
            kwargs['commune__district'] = post['fDistrict']
        else:
            if 'fRegion' in post and post['fRegion'] != '':
                kwargs['commune__district__region'] = post['fRegion']
    if 'fCreede' in post and post['fCreede'] != '':
        cree_de = datetime.strptime(post['fCreede'], "%d/%m/%Y")
        cree_de = datetime.strftime(cree_de, "%Y-%m-%d")
        kwargs['periode__gte'] = cree_de
    if 'fCreea' in post and post['fCreea'] != '':
        cree_a = datetime.strptime(post['fCreea'], "%d/%m/%Y")
        cree_a = datetime.strftime(cree_a, "%Y-%m-%d")
        kwargs['periode__lte'] = cree_a

    records, total_records, display_records = query_datatables(Donnees, columns, post, **kwargs)
    results = []
    for row in records:
        edit_link = '<a href="%s">[Edit]</a>' % (reverse(editer_donnees, args=[row.id]),)
        edit_link = '%s <a href="%s" class="del-link">[Suppr]</a>' % (edit_link, reverse(supprimer_donnees, args=[row.id]),)
        result = dict(
            id = row.id,
            commune = row.commune.nom,
            code = row.commune.code,
            periode = datetime.strftime(row.periode, "%m/%Y"),
            demandes = row.demandes,
            oppositions = row.oppositions,
            resolues = row.resolues,
            certificats = row.certificats,
            femmes = row.femmes,
            surfaces = row.surfaces,
            recettes = row.recettes,
            garanties = row.garanties,
            reconnaissances = row.reconnaissances,
            mutations = row.mutations,
            actions = edit_link,
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords":display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')

def ajax_pivot_table(request):
    # columns titles
    columns = ['nom', 'jan', 'fev', 'mar', 'avr', 'mai', 'jun', 'jul', 'aou', 'sep', 'oct', 'nov', 'dec', 'moy', 'total']

    region_id = 0
    district_id = 0
    # filtering
    post = process_datatables_posted_vars(request.POST)
    kwargs = {}
    # indicateur valide is mandatory
    if 'fIndicateur' in post and  post['fIndicateur'] != '':
        indicateur = str(post['fIndicateur'])
    # year is mandatory
    if 'fAnnee' in post and  post['fAnnee'] != '':
        year = str(post['fAnnee'])
    else:
        year = datetime.now().year - 1
    kwargs['periode__year'] = year

    if 'fCommune' in post and post['fCommune'] != '':
        kwargs['commune'] = str(post['fCommune'])
    else:
        if 'fCode' in post and post['fCode'] != '':
            kwargs['code__icontains'] = post['fCode']
        if 'fDistrict' in post and post['fDistrict'] != '':
            kwargs['commune__district'] = post['fDistrict']
        else:
            if 'fRegion' in post and post['fRegion'] != '':
                kwargs['commune__district__region'] = post['fRegion']

    # get the total rows - year fixed - grouped by commune
    iTotalRecords = Cumul.objects.filter(periode__year=year).values('commune').order_by().annotate(Count('commune'))
    iTotalRecords = len(iTotalRecords)

    # limitting
    lim_start = None
    if 'iDisplayStart' in post and post['iDisplayLength'] != '-1':
        lim_start = int(post['iDisplayStart'])
        lim_num = int(post['iDisplayLength']) + lim_start

    # ordering
    sorts = []
    sort_commune = None
    if 'iSortingCols' in post:
        sort_col = post['iSortCol_0']
        sort_dir = post['sSortDir_0']
        # commune sorting
        if columns[int(sort_col)] == 'nom':
            if sort_dir == "asc":
                sort_qry = 'commune__nom'
            else:
                sort_qry = "-%s" % ('commune__nom',)
            sorts.append(sort_qry)

    # get limited communes
    # kwargs can't be null as year is mandatory
    iTotalDisplayRecords = Cumul.objects.filter(**kwargs).values('commune').order_by().annotate(Count('commune'))
    iTotalDisplayRecords = len(iTotalDisplayRecords)
    if sort_commune is not None:
        if lim_start is not None:
            cumuls = Cumul.objects.filter(**kwargs).values('commune', 'commune__nom').order_by(*sorts).annotate(Count('commune'))[lim_start:lim_num]
        else:
            cumuls = Cumul.objects.filter(**kwargs).values('commune', 'commune__nom').order_by(*sorts).annotate(Count('commune'))
    else:
        if lim_start is not None:
            cumuls = Cumul.objects.filter(**kwargs).values('commune', 'commune__nom').annotate(Count('commune'))[lim_start:lim_num]
        else:
            cumuls = Cumul.objects.filter(**kwargs).values('commune', 'commune__nom').annotate(Count('commune'))

    # querying datas for each commune
    results = []
    for cumul in cumuls:
        ratios = Cumul.objects.filter(periode__year=year, commune=cumul['commune']).values('periode', indicateur).order_by('periode')
        ratio = {'nom': cumul['commune__nom']}
        total = 0
        n = 0
        m = 1
        for row in ratios:
            month = row['periode'].month
            # fill the blanks
            while month > m:
                ratio[columns[m]] = '-'
                m += 1
            if row[indicateur] is not None:
                ratio[columns[month]] = row[indicateur]
                total += row[indicateur]
            else:
                ratio[columns[month]] = '-'
            n += 1
            m += 1
        # fill the blanks
        while m <= 12:
            ratio[columns[m]] = '-'
            m += 1
        ratio['moy'] = round(total / n, 3)
        ratio['total'] = round(total, 3)
        results.append(ratio)

    # les totaux
    total = get_total_indicateur()
    national = total[0][indicateur]
    regional = ''
    district = ''

    if 'fRegion' in post and post['fRegion'] != '':
        region_id = int(post['fRegion'])
        if region_id in total[1]:
            regional = total[1][region_id][indicateur]
            nregion = Commune.objects.filter(district__region=region_id).values('code').annotate(Count('code'))
            nregion= len(nregion)
            regional = round(regional / nregion, 3)

    if 'fDistrict' in post and post['fDistrict'] != '':
        district_id = int(post['fDistrict'])
        if district_id in total[2]:
            district = total[2][district_id][indicateur]
            ndistrict = Commune.objects.filter(district=district_id).values('code').annotate(Count('code'))
            ndistrict = len(ndistrict)
            district = round(district / ndistrict, 3)


    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": iTotalRecords, "iTotalDisplayRecords":iTotalDisplayRecords, "sEcho": sEcho, "aaData": results,
               "national": national, "regional": regional, "district": district}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')

def export_indicateurs(request):
    columns = [u'Commune', u'Code', u'Période', u'Demandes', u'Oppositions', u'Résolues', u'Certificats', u'Femmes', u'Surfaces', u'Recettes', u'Garanties', u'Reconnaissances', u'Mutations']
    dataset = Donnees.objects.filter_for_xls(request.GET)
    response = export_excel(columns, dataset, 'indicateurs')
    return response

def export_ratios(request):
    columns = [u'Commune', u'Jan', u'Fév', u'Mar', u'Avr', u'Mai', u'Jun', u'Jul', u'Sep', u'Oct', u'Nov', u'Déc', 'Moy', 'Tot']
    dataset = Donnees.objects.filter_ratio_for_xls(request.GET)
    response = export_excel(columns, dataset, 'ratio')
    return response

def ajax_ratios_localite(request):
    # columns titles
    columns = ['localite', 'certificats', 'femmes', 'conflits', 'resolus', 'surface']

    # filtering
    post = process_datatables_posted_vars(request.POST)
    kwargs = {}
    # year is mandatory
    if 'fAnnee' in post and  post['fAnnee'] != '':
        year = str(post['fAnnee'])
    else:
        year = datetime.now().year - 1
    kwargs['periode__year'] = year

    records = Cumul.objects.filter(**kwargs).values('periode', 'rcertificats', 'rfemmes', 'rconflits', 'rresolus', 'rsurface').order_by('periode')
    results = []
    for row in records:
        result = dict(
            id = row.id,
            commune = row.commune.nom,
            code = row.commune.code,
            periode = datetime.strftime(row.periode, "%m/%Y"),
            demandes = row.demandes,
            oppositions = row.oppositions,
            resolues = row.resolues,
            certificats = row.certificats,
            femmes = row.femmes,
            surfaces = row.surfaces,
            recettes = row.recettes,
            garanties = row.garanties,
            reconnaissances = row.reconnaissances,
            mutations = row.garanties
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords":display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')

def _remove_none(data):
    if data.oppositions is None:
        data.oppositions = 0
    if data.resolues is None:
        data.resolues = 0
    if data.certificats is None:
        data.certificats = 0
    if data.femmes is None:
        data.femmes = 0
    if data.recettes is None:
        data.recettes = 0
    if data.mutations is None:
        data.mutations = 0
    if data.surfaces is None:
        data.surfaces = 0
    if data.garanties is None:
        data.garanties = 0
    if data.reconnaissances is None:
        data.reconnaissances = 0
    if data.rcertificats is None:
        data.rcertificats = 0
    if data.rfemmes is None:
        data.rfemmes = 0
    if data.rresolus is None:
        data.rresolus = 0
    if data.rconflits is None:
        data.rconflits = 0
    if data.rsurface is None:
        data.rsurface = 0
    return data


def get_total_indicateur():
    # select distincts commune having data
    cumuls = Cumul.objects.all().values('commune').order_by('commune__district__region__code', 'commune__district__code').annotate(Count('commune'))
    n = len(cumuls)

    region = {}
    district = {}
    national = dict(demandes=0, oppositions=0, resolues=0, certificats=0, femmes=0,
                    recettes=0, mutations=0, surfaces=0, garanties=0, reconnaissances=0,
                    rcertificats=0, rfemmes=0, rresolus=0, rconflits=0, rsurface=0)
    for cumul in cumuls:
        # select the last record for each commune
        last_record = Cumul.objects.filter(commune=cumul['commune']).order_by('-periode')[:1]
        last_record = _remove_none(last_record[0])
        region_code = last_record.commune.district.region.id
        district_code = last_record.commune.district.id
        
        #total regional
        if region_code in region:
            region[region_code]['demandes'] += last_record.demandes
            region[region_code]['oppositions'] += last_record.oppositions
            region[region_code]['resolues'] += last_record.resolues
            region[region_code]['certificats'] += last_record.certificats
            region[region_code]['femmes'] += last_record.femmes
            region[region_code]['recettes'] += last_record.recettes
            region[region_code]['mutations'] += last_record.mutations
            region[region_code]['surfaces'] += last_record.surfaces
            region[region_code]['garanties'] += last_record.garanties
            region[region_code]['reconnaissances'] += last_record.reconnaissances
            region[region_code]['rcertificats'] += last_record.rcertificats
            region[region_code]['rfemmes'] += last_record.rfemmes
            region[region_code]['rresolus'] += last_record.rresolus
            region[region_code]['rconflits'] += last_record.rconflits
            region[region_code]['rsurface'] += last_record.rsurface            
        else:
            data = dict(demandes=last_record.demandes,
            oppositions=last_record.oppositions,
            resolues=last_record.resolues,
            certificats=last_record.certificats,
            femmes=last_record.femmes,
            recettes=last_record.recettes,
            mutations=last_record.mutations,
            surfaces=last_record.surfaces,
            garanties=last_record.garanties,
            reconnaissances=last_record.reconnaissances,
            rcertificats=last_record.rcertificats,
            rfemmes=last_record.rfemmes,
            rresolus=last_record.rresolus,
            rconflits=last_record.rconflits,
            rsurface=last_record.rsurface)
            region[region_code] = data

        #total district
        if district_code in district:
            district[district_code]['demandes'] += last_record.demandes
            district[district_code]['oppositions'] += last_record.oppositions
            district[district_code]['resolues'] += last_record.resolues
            district[district_code]['certificats'] += last_record.certificats
            district[district_code]['femmes'] += last_record.femmes
            district[district_code]['recettes'] += last_record.recettes
            district[district_code]['mutations'] += last_record.mutations
            district[district_code]['surfaces'] += last_record.surfaces
            district[district_code]['garanties'] += last_record.garanties
            district[district_code]['reconnaissances'] += last_record.reconnaissances
            district[district_code]['rcertificats'] += last_record.rcertificats
            district[district_code]['rfemmes'] += last_record.rfemmes
            district[district_code]['rresolus'] += last_record.rresolus
            district[district_code]['rconflits'] += last_record.rconflits
            district[district_code]['rsurface'] += last_record.rsurface            
        else:
            data = dict(demandes=last_record.demandes,
            oppositions=last_record.oppositions,
            resolues=last_record.resolues,
            certificats=last_record.certificats,
            femmes=last_record.femmes,
            recettes=last_record.recettes,
            mutations=last_record.mutations,
            surfaces=last_record.surfaces,
            garanties=last_record.garanties,
            reconnaissances=last_record.reconnaissances,
            rcertificats=last_record.rcertificats,
            rfemmes=last_record.rfemmes,
            rresolus=last_record.rresolus,
            rconflits=last_record.rconflits,
            rsurface=last_record.rsurface)
            district[district_code] = data

        # national
        national['demandes'] += last_record.demandes
        national['oppositions'] += last_record.oppositions
        national['resolues'] += last_record.resolues
        national['certificats'] += last_record.certificats
        national['femmes'] += last_record.femmes
        national['recettes'] += last_record.recettes
        national['mutations'] += last_record.mutations
        national['surfaces'] += last_record.surfaces
        national['garanties'] += last_record.garanties
        national['reconnaissances'] += last_record.reconnaissances
        national['rcertificats'] += last_record.rcertificats
        national['rfemmes'] += last_record.rfemmes
        national['rresolus'] += last_record.rresolus
        national['rconflits'] += last_record.rconflits
        national['rsurface'] += last_record.rsurface

        national['rcertificats'] = round(national['rcertificats'] / n, 3)
        national['rfemmes'] = round(national['rfemmes'] / n, 3)
        national['rresolus'] = round(national['rresolus'] / n, 3)
        national['rconflits'] = round(national['rconflits'] / n, 3)
        national['rsurface'] = round(national['rsurface'] / n, 3)

    return (national, region, district)


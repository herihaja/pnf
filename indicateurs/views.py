# -*- coding: utf-8 -*-
from __future__ import division
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from donnees.models import Donnees, Cumul
from helpers import process_datatables_posted_vars, query_datatables, export_excel
from indicateurs.forms import FiltreIndicateursForm, FiltreIndicateurForm, FiltreRatioForm
from django.db.models import Count
import simplejson
from datetime import datetime

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
    return render_to_response('layout_list.html', {"form": form, "title": title, "page_js": page_js},
                              context_instance=RequestContext(request))

def ajax_indicateurs(request):
    # columns titles
    columns = ['commune', 'code', 'periode', 'demandes', 'oppositions', 'resolues', 'certificats', 'femmes', 'surfaces', 'recettes', 'garanties', 'reconnaissances', 'mutations']

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

def ajax_pivot_table(request):
    # columns titles
    columns = ['nom', 'jan', 'fev', 'mar', 'avr', 'mai', 'jun', 'jul', 'aou', 'sep', 'oct', 'nov', 'dec', 'moy', 'total']

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
        ratio['moy'] = round(total / n, 2)
        ratio['total'] = total
        results.append(ratio)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": iTotalRecords, "iTotalDisplayRecords":iTotalDisplayRecords, "sEcho": sEcho, "aaData": results}
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
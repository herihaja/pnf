# -*- coding: utf-8 -*-
from __future__ import division
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from donnees.models import Donnees, Cumul
from helpers import process_datatables_posted_vars
from indicateurs.forms import FiltreIndicateursForm, FiltreIndicateurForm, FiltreRatioForm
from django.db.models import Count
import simplejson
from datetime import datetime

def indicateurs_par_date(request):
    if request.method == 'GET':
        form = FiltreIndicateursForm()
    else:
        form = FiltreIndicateursForm(request.POST)
    return render_to_response('indicateurs/lister_indicateurs.html', {"form": form, "title": "Indicateurs par localités"}, context_instance=RequestContext(request))

def indicateur_par_date(request):
    if request.method == 'GET':
        form = FiltreIndicateurForm(initial={'annee': datetime.now().year - 1})
    else:
        form = FiltreIndicateurForm(request.POST)
    return render_to_response('indicateurs/liste.html', {"form": form, "title": "Indicateur par année"}, context_instance=RequestContext(request))

def ratio(request, ratio, title):
    if request.method == 'GET':
        form = FiltreRatioForm(initial={'indicateur': ratio, 'annee': datetime.now().year - 1})
    else:
        form = FiltreRatioForm(request.POST)
    return render_to_response('indicateurs/liste.html', {"form": form, "title": title}, context_instance=RequestContext(request))

def ajax_indicateurs(request):
    # columns titles
    columns = ['commune', 'code', 'periode', 'demandes', 'oppositions', 'resolues', 'certificats', 'femmes', 'surfaces', 'recettes', 'garanties', 'reconnaissances', 'mutations']

    # filtering
    posted = process_datatables_posted_vars(request.POST)
    # valide true
    kwargs = {'valide': True}

    if 'fCommune' in posted and posted['fCommune'] != '':
        kwargs['nom__icontains'] = str(posted['fCommune'])
    else:
        if 'fCode' in posted and posted['fCode'] != '':
            kwargs['commune__code__icontains'] = posted['fCode']
        if 'fDistrict' in posted and posted['fDistrict'] != '':
            kwargs['commune__district'] = posted['fDistrict']
        else:
            if 'fRegion' in posted and posted['fRegion'] != '':
                kwargs['commune__district__region'] = posted['fRegion']

    # ordering
    sorts = []
    if 'iSortingCols' in posted:
        for i in range(0, int(posted['iSortingCols'])):
            sort_col = "iSortCol_%s" % (i,)
            sort_dir = posted["sSortDir_%s" % (i,)]
            if columns[int(posted[sort_col])] == 'code':  # code
                if sort_dir == "asc":
                    sort_qry = "commune__code"
                else:
                    sort_qry = "-commune__code"
            else:
                if sort_dir == "asc":
                    sort_qry = columns[int(posted[sort_col])]
                else:
                    sort_qry = "-%s" % (columns[int(posted[sort_col])],)
            sorts.append(sort_qry)

    # limitting
    lim_start = None
    if 'iDisplayStart' in posted and posted['iDisplayLength'] != '-1':
        lim_start = int(posted['iDisplayStart'])
        lim_num = int(posted['iDisplayLength']) + lim_start

    # querying
    iTotalRecords = Cumul.objects.filter(valide=True).count()
    if len(kwargs) > 0:
        if len(sorts) > 0:
            if lim_start is not None:
                donnees = Cumul.objects.filter(**kwargs).order_by(*sorts)[lim_start:lim_num]
            else:
                donnees = Cumul.objects.filter(**kwargs).order_by(*sorts)
        else:
            if lim_start is not None:
                donnees = Cumul.objects.filter(**kwargs)[lim_start:lim_num]
            else:
                donnees = Cumul.objects.filter(**kwargs)
        iTotalDisplayRecords = Cumul.objects.filter(**kwargs).count()
    else:
        if len(sorts) > 0:
            if lim_start is not None:
                donnees = Cumul.objects.all().order_by(*sorts)[lim_start:lim_num]
            else:
                donnees = Cumul.objects.all().order_by(*sorts)
        else:
            if lim_start is not None:
                donnees = Cumul.objects.all()[lim_start:lim_num]
            else:
                donnees = Cumul.objects.all()
        iTotalDisplayRecords = iTotalRecords

    results = []

    for row in donnees:
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

    sEcho = int(posted['sEcho'])
    results = {"iTotalRecords": iTotalRecords, "iTotalDisplayRecords":iTotalDisplayRecords, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')

def ajax_pivot_table(request):
    # columns titles
    columns = ['nom', 'jan', 'fev', 'mar', 'avr', 'mai', 'jun', 'jul', 'aou', 'sep', 'oct', 'nov', 'dec', 'moy', 'total']

    # filtering
    posted = process_datatables_posted_vars(request.POST)
    kwargs = {}
    # indicateur valide is mandatory
    if 'fIndicateur' in posted and  posted['fIndicateur'] != '':
        indicateur = str(posted['fIndicateur'])
    if 'fValide' in posted and  posted['fValide'] != '':
        kwargs['valide'] = str(posted['fValide'])
    # year is mandatory
    if 'fAnnee' in posted and  posted['fAnnee'] != '':
        year = str(posted['fAnnee'])
    else:
        #Todo : default year to current -1
        year = '2010'
    kwargs['periode__year'] = year

    if 'fCommune' in posted and posted['fCommune'] != '':
        kwargs['commune'] = str(posted['fCommune'])
    else:
        if 'fCode' in posted and posted['fCode'] != '':
            kwargs['code__icontains'] = posted['fCode']
        if 'fDistrict' in posted and posted['fDistrict'] != '':
            kwargs['commune__district'] = posted['fDistrict']
        else:
            if 'fRegion' in posted and posted['fRegion'] != '':
                kwargs['commune__district__region'] = posted['fRegion']

    # get the total rows - year fixed - grouped by commune
    iTotalRecords = Cumul.objects.filter(periode__year=year).values('commune').order_by().annotate(Count('commune'))
    iTotalRecords = len(iTotalRecords)

    # limitting
    lim_start = None
    if 'iDisplayStart' in posted and posted['iDisplayLength'] != '-1':
        lim_start = int(posted['iDisplayStart'])
        lim_num = int(posted['iDisplayLength']) + lim_start

    # ordering
    sorts = []
    sort_commune = None
    if 'iSortingCols' in posted:
        sort_col = posted['iSortCol_0']
        sort_dir = posted['sSortDir_0']
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

    sEcho = int(posted['sEcho'])
    results = {"iTotalRecords": iTotalRecords, "iTotalDisplayRecords":iTotalDisplayRecords, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')

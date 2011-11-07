# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from localites.forms import FiltreCommuneForm
from localites.models import Commune
import simplejson
from localites.views import supprimer_commune, editer_commune
from django.views.decorators.csrf import csrf_exempt

def lister(request):
    if request.method == 'GET':
        form = FiltreCommuneForm()
    else:
        form = FiltreCommuneForm(request.POST)
    return render_to_response('datatables/liste.html', {"form": form}, context_instance=RequestContext(request))

def ajax(request):
    # columns titles
    columns = ['nom', 'code', 'district__region', 'district', 'actions']

    # filtering
    posted_data = request.POST
    posted = {}
    num_data = len(posted_data) // 2 -1
    for i in range (0,  num_data):
        key = "data[%s][name]" % (i,)
        value = "data[%s][value]" % (i,)
        posted[posted_data[key]] = posted_data[value]
    
    kwargs = {}
    if 'fCommune' in posted and posted['fCommune'] != '':
        kwargs['nom__icontains'] = str(posted['fCommune'])
    if 'fCode' in posted and posted['fCode'] != '':
        kwargs['code__icontains'] = posted['fCode']
    if 'fDistrict' in posted and posted['fDistrict'] != '':
        kwargs['district'] = posted['fDistrict']
    else:
        if 'fRegion' in posted and posted['fRegion'] != '':
            kwargs['district__region'] = posted['fRegion']

    # ordering
    sorts = []
    if 'iSortingCols' in posted:
        for i in range(0, int(posted['iSortingCols'])):
            sort_col = "iSortCol_%s" % (i,)
            sort_dir = posted["sSortDir_%s" % (i,)]
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
    iTotalRecords = Commune.objects.count()
    if len(kwargs) > 0:
        if len(sorts) > 0:
            if lim_start is not None:
                commune = Commune.objects.filter(**kwargs).order_by(*sorts)[lim_start:lim_num]
            else:
                commune = Commune.objects.filter(**kwargs).order_by(*sorts)
        else:
            if lim_start is not None:
                commune = Commune.objects.filter(**kwargs)[lim_start:lim_num]
            else:
                commune = Commune.objects.filter(**kwargs)
        iTotalDisplayRecords = Commune.objects.filter(**kwargs).count()
    else:
        if len(sorts) > 0:
            if lim_start is not None:
                commune = Commune.objects.all().order_by(*sorts)[lim_start:lim_num]
            else:
                commune = Commune.objects.all().order_by(*sorts)
        else:
            if lim_start is not None:
                commune = Commune.objects.all()[lim_start:lim_num]
            else:
                commune = Commune.objects.all()
        iTotalDisplayRecords = iTotalRecords

    results = []

    for row in commune:
        edit_link = '<a href="%s">[Edit]</a>' % (reverse(editer_commune, args=[row.id]),)
        edit_link = '%s <a href="%s" class="del-link">[Suppr]</a>' % (edit_link, reverse(supprimer_commune, args=[row.id]),)
        result = dict(
            id = row.id,
            nom = row.nom,
            code = row.code,
            region = row.district.region.nom,
            district = row.district.nom,
            actions = edit_link,
        )
        results.append(result)

    sEcho = int(posted['sEcho'])
    results = {"iTotalRecords": iTotalRecords, "iTotalDisplayRecords":iTotalDisplayRecords, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')
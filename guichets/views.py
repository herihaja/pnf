# -*- coding: utf-8 -*-
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from guichets.models import Guichet
from guichets.forms import GuichetForm, FiltreGuichetForm
from helpers import export_excel, process_datatables_posted_vars
import simplejson

def lister_guichet(request):
    if request.method == 'GET':
        form = FiltreGuichetForm()
    else:
        form = FiltreGuichetForm(request.POST)
    return render_to_response('guichets/lister_guichet.html', {"form": form}, context_instance=RequestContext(request))

def ajouter_guichet(request):
    if request.method == 'GET':
        form = GuichetForm()
        return render_to_response('guichets/ajouter_guichet.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = GuichetForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_guichet))
    else:
        return render_to_response('guichets/ajouter_guichet.html', {'form': form},
                                  context_instance=RequestContext(request))

def editer_guichet(request, guichet_id=None):
    obj = get_object_or_404(Guichet, pk=guichet_id)

    if request.method == 'GET':
        form = GuichetForm(instance=obj)
        return render_to_response('guichets/ajouter_guichet.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = GuichetForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_guichet))
    else:
        return render_to_response('guichets/ajouter_guichet.html', {'form': form},
                                  context_instance=RequestContext(request))

def supprimer_guichet(request, guichet_id=None):
    obj = get_object_or_404(Guichet, pk=guichet_id)
    obj.delete()
    return HttpResponseRedirect(reverse(lister_guichet))

def export(rows):
    header = ['Commune', 'agf1',  'mobile1', 'agf2', 'mobile2', 'etat']
    liste = []
    for row in rows:
        cleaned_row = [row.commune.code, row.agf1, row.mobile1, row.agf2, row.mobile2, row.etat]
        liste.append(cleaned_row)
    ret = export_excel(header, liste, 'guichets')
    return ret

def ajax_guichet(request):
    CHOIX_ETAT = {
        '1': 'Actif',
        '2': 'Non actif',
        '3': 'Fermé',
        '4': 'En cours',
    }
    # columns titles
    columns = ['commune', 'code', 'creation', 'agf1', 'num1', 'password1', 'agf2', 'num2', 'password2', 'etat', 'actions']

    # filtering
    posted = process_datatables_posted_vars(request.POST)

    kwargs = {}
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
    if 'fAgf1' in posted and posted['fAgf1'] != '':
        kwargs['agf1__icontains'] = str(posted['fAgf1'])
    if 'fMobile1' in posted and posted['fMobile1'] != '':
        kwargs['mobile1__icontains'] = str(posted['fMobile1'])
    if 'fAgf2' in posted and posted['fAgf2'] != '':
        kwargs['agf2__icontains'] = str(posted['fAgf2'])
    if 'fMobile2' in posted and posted['fMobile2'] != '':
        kwargs['mobile2__icontains'] = str(posted['fMobile2'])
    if 'fCreede' in posted and posted['fCreede'] != '':
        cree_de = datetime.strptime(posted['fCreede'], "%d/%m/%Y")
        cree_de = datetime.strftime(cree_de, "%Y-%m-%d")
        kwargs['creation__gte'] = cree_de
    if 'fCreea' in posted and posted['fCreea'] != '':
        cree_a = datetime.strptime(posted['fCreea'], "%d/%m/%Y")
        cree_a = datetime.strftime(cree_a, "%Y-%m-%d")
        kwargs['creation__lte'] = cree_a

    # ordering
    sorts = []
    if 'iSortingCols' in posted:
        for i in range(0, int(posted['iSortingCols'])):
            sort_col = "iSortCol_%s" % (i,)
            sort_dir = posted["sSortDir_%s" % (i,)]
            if columns[int(posted[sort_col])] == 'code':
                if sort_dir == "asc":
                    sort_qry = 'commune__code'
                else:
                    sort_qry = '-commune__code'
                sorts.append(sort_qry)
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
    iTotalRecords = Guichet.objects.count()
    if len(kwargs) > 0:
        if len(sorts) > 0:
            if lim_start is not None:
                guichet = Guichet.objects.filter(**kwargs).order_by(*sorts)[lim_start:lim_num]
            else:
                guichet = Guichet.objects.filter(**kwargs).order_by(*sorts)
        else:
            if lim_start is not None:
                guichet = Guichet.objects.filter(**kwargs)[lim_start:lim_num]
            else:
                guichet = Guichet.objects.filter(**kwargs)
        iTotalDisplayRecords = Guichet.objects.filter(**kwargs).count()
    else:
        if len(sorts) > 0:
            if lim_start is not None:
                guichet = Guichet.objects.all().order_by(*sorts)[lim_start:lim_num]
            else:
                guichet = Guichet.objects.all().order_by(*sorts)
        else:
            if lim_start is not None:
                guichet = Guichet.objects.all()[lim_start:lim_num]
            else:
                guichet = Guichet.objects.all()
        iTotalDisplayRecords = iTotalRecords

    results = []

    for row in guichet:
        edit_link = '<a href="%s">[Edit]</a>' % (reverse(editer_guichet, args=[row.id]),)
        edit_link = '%s <a href="%s" class="del-link">[Suppr]</a>' % (edit_link, reverse(supprimer_guichet, args=[row.id]),)
        if len(row.password1) > 0:
            password1 = 'Oui'
        else:
            password1 = 'Non'
        if row.agf2 is not None:
            if len(row.password2) > 0:
                password2 = 'Oui'
            else:
                password2 = 'Non'
        else:
            password2 = ''

        result = dict(
            commune = row.commune.nom,
            code = row.commune.code,
            creation = datetime.strftime(row.creation, "%d-%m-%Y"),
            agf1 = row.agf1,
            num1 = row.mobile1,
            password1 = password1,
            agf2 = row.agf2,
            num2 = row.mobile2,
            password2 = password2,
            etat = CHOIX_ETAT[row.etat],
            actions = edit_link,
        )
        results.append(result)

    sEcho = int(posted['sEcho'])
    results = {"iTotalRecords": iTotalRecords, "iTotalDisplayRecords":iTotalDisplayRecords, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')
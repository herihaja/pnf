# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from donnees.models import Donnees, Cumul
from donnees.forms import DonneesForm, FiltreDonneesForm
from helpers import paginate, export_excel, process_datatables_posted_vars
import simplejson
from datetime import datetime

def lister_donnees(request):
    if request.method == 'GET':
            form = FiltreDonneesForm()
    else:
        form = FiltreDonneesForm(request.POST)
    return render_to_response('donnees/lister_donnees.html', {"form": form}, context_instance=RequestContext(request))

def _create_query(field, value):
    value = value.strip()
    if value[0:1] == '>':
        if value[1:2] == '=':
            key = '%s__gte' % (field,)
            value = value[2:].lstrip()
        else:
            key = '%s__gt' % (field,)
            value = value[1:].lstrip()
    elif value[0:1] == '<':
        if value[1:2] == '=':
            key = '%s__lte' % (field,)
            value = value[2:].lstrip()
        else:
            key = '%s__lt' % (field,)
            value = value[1:].lstrip()
    elif value[0:1] == '=' and (value[1:2] != '<' or value[1:2] != '>'):
        key = field
        value = value[1:].lstrip()
    else:
        key = field
        value = value
    return key, value

def ajax_donnees(request):
    # columns titles
    columns = ['commune', 'code', 'periode', 'demandes', 'oppositions', 'resolues', 'certificats', 'femmes', 'surfaces', 'recettes', 'garanties', 'reconnaissances', 'mutations', 'valide', 'actions']

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

    # filtering of indicateurs
    for i in range(3, 12):
        posted_key = 'f%s' % (columns[i].capitalize(),)
        if posted_key in posted and posted[posted_key] != '':
            key, value = _create_query(columns[i], posted[posted_key])
            kwargs[key] = value

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
    iTotalRecords = Donnees.objects.filter(valide=True).count()
    if len(kwargs) > 0:
        if len(sorts) > 0:
            if lim_start is not None:
                donnees = Donnees.objects.filter(**kwargs).order_by(*sorts)[lim_start:lim_num]
            else:
                donnees = Donnees.objects.filter(**kwargs).order_by(*sorts)
        else:
            if lim_start is not None:
                donnees = Donnees.objects.filter(**kwargs)[lim_start:lim_num]
            else:
                donnees = Donnees.objects.filter(**kwargs)
        iTotalDisplayRecords = Donnees.objects.filter(**kwargs).count()
    else:
        if len(sorts) > 0:
            if lim_start is not None:
                donnees = Donnees.objects.all().order_by(*sorts)[lim_start:lim_num]
            else:
                donnees = Donnees.objects.all().order_by(*sorts)
        else:
            if lim_start is not None:
                donnees = Donnees.objects.all()[lim_start:lim_num]
            else:
                donnees = Donnees.objects.all()
        iTotalDisplayRecords = iTotalRecords

    results = []

    for row in donnees:
        edit_link = '<a href="%s">[Edit]</a>' % (reverse(editer_donnees, args=[row.id]),)
        edit_link = '%s <a href="%s" class="del-link">[Suppr]</a>' % (edit_link, reverse(supprimer_donnees, args=[row.id]),)
        if row.valide:
            valide = 'Oui'
        else:
            valide = 'Non'
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
            mutations = row.garanties,
            valide = valide,
            actions = edit_link,
        )
        results.append(result)

    sEcho = int(posted['sEcho'])
    results = {"iTotalRecords": iTotalRecords, "iTotalDisplayRecords":iTotalDisplayRecords, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')

def ajouter_donnees(request):
    if request.method == 'GET':
        form = DonneesForm()
        return render_to_response('donnees/ajouter_donnees.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = DonneesForm(request.POST)
    if form.is_valid():
        if form.save():
            message = "Vos données ont été ajoutées avec succès."
            return HttpResponseRedirect(reverse(lister_donnees))
    else:
        return render_to_response('donnees/ajouter_donnees.html', {'form': form},
                                  context_instance=RequestContext(request))

def editer_donnees(request, donnee_id=None):
    obj = get_object_or_404(Donnees, pk=donnee_id)

    if request.method == 'GET':
        form = DonneesForm(instance=obj)
        return render_to_response('donnees/ajouter_donnees.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = DonneesForm(request.POST, instance=obj)
    if form.is_valid():
        if form.save():
            message = "Vos données ont été mises à jour avec succès."
            return HttpResponseRedirect(reverse(lister_donnees))
        else:
            message = "Veuillez d'abord enregistrer les données des mois précédents."
        return render_to_response('donnees/ajouter_donnees.html', {'form': form, 'message': message},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('donnees/ajouter_donnees.html', {'form': form},
                                  context_instance=RequestContext(request))

def supprimer_donnees(request, donnee_id=None):
    obj = get_object_or_404(Donnees, pk=donnee_id)
    obj.delete()
    json = simplejson.dumps([{'message': 'Enregistrement supprimé'}])
    return HttpResponse(json, mimetype='application/json')



def lister_cumuls(request):
    if request.method == 'GET':
            form = FiltreDonneesForm()
    else:
        form = FiltreDonneesForm(request.POST)
    return render_to_response('donnees/lister_cumul.html', {"form": form}, context_instance=RequestContext(request))

def ajax_cumuls(request):
    # columns titles
    columns = ['commune', 'code', 'periode', 'demandes', 'oppositions', 'resolues', 'certificats', 'femmes', 'surfaces', 'recettes', 'garanties', 'reconnaissances', 'mutations']

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

    # filtering of indicateurs
    for i in range(3, 12):
        posted_key = 'f%s' % (columns[i].capitalize(),)
        if posted_key in posted and posted[posted_key] != '':
            key, value = _create_query(columns[i], posted[posted_key])
            kwargs[key] = value

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
    iTotalRecords = Donnees.objects.filter(valide=True).count()
    if len(kwargs) > 0:
        if len(sorts) > 0:
            if lim_start is not None:
                cumul = Donnees.objects.filter(**kwargs).order_by(*sorts)[lim_start:lim_num]
            else:
                cumul = Donnees.objects.filter(**kwargs).order_by(*sorts)
        else:
            if lim_start is not None:
                cumul = Donnees.objects.filter(**kwargs)[lim_start:lim_num]
            else:
                cumul = Donnees.objects.filter(**kwargs)
        iTotalDisplayRecords = Donnees.objects.filter(**kwargs).count()
    else:
        if len(sorts) > 0:
            if lim_start is not None:
                cumul = Donnees.objects.all().order_by(*sorts)[lim_start:lim_num]
            else:
                cumul = Donnees.objects.all().order_by(*sorts)
        else:
            if lim_start is not None:
                cumul = Donnees.objects.all()[lim_start:lim_num]
            else:
                cumul = Donnees.objects.all()
        iTotalDisplayRecords = iTotalRecords

    results = []

    for row in cumul:
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
            mutations = row.garanties,
        )
        results.append(result)

    sEcho = int(posted['sEcho'])
    results = {"iTotalRecords": iTotalRecords, "iTotalDisplayRecords":iTotalDisplayRecords, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')

def _export(rows):
    header = ['Commune', 'Sms','Periode', 'Demandes', 'Oppositions', 'Resolues', 'Certificats', 'Femmes', 'Recettes', 'Mutations', 'Surfaces', 'Garanties', 'Reconnaissance', 'Valide']
    liste = []
    for row in rows:
        cleaned_row = [row.commune.nom, row.sms.message, row.periode, row.demandes, row.oppositions, row.resolues, row.certificats, row.femmes, row.recettes, row.mutations, row.surfaces, row.garanties, row.reconnaissances, row.valide]
        liste.append(cleaned_row)
    ret = export_excel(header, liste, 'données')
    return ret

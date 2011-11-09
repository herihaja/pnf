# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from bailleurs.models import Bailleur
from bailleurs.forms import BailleurForm, FiltreBailleurForm
from helpers import paginate, export_excel, process_datatables_posted_vars
import simplejson

def lister_bailleur(request):
    bailleur_liste = []

    if request.method == 'GET':
        form = FiltreBailleurForm()
        rows = Bailleur.objects.all()
        page = int(request.GET.get('page', '1'))
    else:
        form = FiltreBailleurForm(request.POST)
        rows = Bailleur.objects.filtrer(request)
        page = int(request.POST['page'])
        if request.POST['action'] == 'export':
            return export(rows)

    if rows is not None:
        for row in rows:
            bailleur_id = row.id
            lien_editer = reverse(editer_bailleur, args=[bailleur_id])
            lien_supprimer = reverse(supprimer_bailleur, args=[bailleur_id])
            bailleur = dict(
                id=row.id,
                nom=row.nom,
                lien_editer=lien_editer,
                lien_supprimer=lien_supprimer
            )
            bailleur_liste.append(bailleur)

    bailleurs = paginate(bailleur_liste, 25, page)

    return render_to_response('bailleurs/lister_bailleur.html', {"bailleurs": bailleurs, "form": form},
                              context_instance=RequestContext(request))

def ajouter_bailleur(request):
    if request.method == 'GET':
        form = BailleurForm()
        return render_to_response('bailleurs/ajouter_bailleur.html', {'form': form, 'title': 'Ajouter un bailleur'},
                                  context_instance=RequestContext(request))

    form = BailleurForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_bailleur))
    else:
        return render_to_response('bailleurs/ajouter_bailleur.html', {'form': form, 'title': 'Ajouter un bailleur'},
                                  context_instance=RequestContext(request))

def editer_bailleur(request, bailleur_id=None):
    obj = get_object_or_404(Bailleur, pk=bailleur_id)

    if request.method == 'GET':
        form = BailleurForm(instance=obj)
        return render_to_response('bailleurs/ajouter_bailleur.html', {'form': form, 'title': 'Editer un bailleur'},
                                  context_instance=RequestContext(request))

    form = BailleurForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_bailleur))
    else:
        return render_to_response('bailleurs/ajouter_bailleur.html', {'form': form, 'title': 'Editer un bailleur'},
                                  context_instance=RequestContext(request))

def supprimer_bailleur(request, bailleur_id=None):
    obj = get_object_or_404(Bailleur, pk=bailleur_id)
    obj.delete()
    #return HttpResponseRedirect(reverse(lister_bailleur))
    json = simplejson.dumps([{'message': 'Enregistrement supprimé'}])
    return HttpResponse(json, mimetype='application/json')

def export(rows):
    header = ['Id', 'Nom']
    liste = []
    for row in rows:
        cleaned_row = [row.id, row.nom]
        liste.append(cleaned_row)
    ret = export_excel(header, liste, 'bailleurs')
    return ret

def ajax_bailleur(request):
    # columns titles
    columns = ['nom', 'actions']

    # filtering
    posted = process_datatables_posted_vars(request.POST)

    kwargs = {}
    if 'fNom' in posted and posted['fNom'] != '':
        kwargs['nom__icontains'] = posted['fNom']

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
    iTotalRecords = Bailleur.objects.count()
    if len(sorts) > 0:
        if lim_start is not None:
            bailleur = Bailleur.objects.filter(**kwargs).order_by(*sorts)[lim_start:lim_num]
        else:
            bailleur = Bailleur.objects.filter(**kwargs).order_by(*sorts)
    else:
        if lim_start is not None:
            bailleur = Bailleur.objects.filter(**kwargs)[lim_start:lim_num]
        else:
            bailleur = Bailleur.objects.filter(**kwargs)
    iTotalDisplayRecords = Bailleur.objects.filter(**kwargs).count()

    results = []

    for row in bailleur:
        edit_link = '<a href="%s">[Edit]</a>' % (reverse(editer_bailleur, args=[row.id]),)
        edit_link = '%s <a href="%s" class="del-link">[Suppr]</a>' % (edit_link, reverse(supprimer_bailleur, args=[row.id]),)
        result = dict(
            nom = row.nom,
            actions = edit_link,
        )
        results.append(result)

    sEcho = int(posted['sEcho'])
    results = {"iTotalRecords": iTotalRecords, "iTotalDisplayRecords":iTotalDisplayRecords, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')
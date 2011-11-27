# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from projets.models import Projet
from projets.forms import ProjetForm, FiltreProjetForm
from helpers import export_excel, process_datatables_posted_vars, query_datatables
import simplejson

def lister_projet(request):
    if request.method == 'GET':
        form = FiltreProjetForm()
    else:
        form = FiltreProjetForm(request.POST)
    header_link = '<a href="%s">&raquo; Ajouter un projet</a>' % (reverse(ajouter_projet),)
    page_js = '/media/js/projets/projets.js'
    title = 'Liste des projets'
    return render_to_response('layout_list.html', {"form": form, "title": title, "page_js": page_js, "header_link": header_link},
                              context_instance=RequestContext(request))

def ajouter_projet(request):
    if request.method == 'GET':
        form = ProjetForm()
        return render_to_response('projets/ajouter_projet.html', {'form': form, 'title': 'Ajouter un projet'},
                                  context_instance=RequestContext(request))

    form = ProjetForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_projet))
    else:
        return render_to_response('projets/ajouter_projet.html', {'form': form, 'title': 'Ajouter un projet'},
                                  context_instance=RequestContext(request))

def editer_projet(request, projet_id=None):
    obj = get_object_or_404(Projet, pk=projet_id)

    if request.method == 'GET':
        form = ProjetForm(instance=obj)
        return render_to_response('projets/ajouter_projet.html', {'form': form, 'title': 'Editer un projet'},
                                  context_instance=RequestContext(request))

    form = ProjetForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_projet))
    else:
        return render_to_response('projets/ajouter_projet.html', {'form': form, 'title': 'Editer un projet'},
                                  context_instance=RequestContext(request))

def supprimer_projet(request, projet_id=None):
    obj = get_object_or_404(Projet, pk=projet_id)
    obj.delete()
    json = simplejson.dumps([{'message': 'Enregistrement supprimé'}])
    return HttpResponse(json, mimetype='application/json')

def export_projet(request):
    columns = [u'Nom', u'Bailleur']
    dataset = Projet.objects.filter_for_xls(request.GET)
    response = export_excel(columns, dataset, 'projets')
    return response

def ajax_projet(request):
    # columns titles
    columns = ['nom', 'bailleurs', 'actions']

    # filtering
    post = process_datatables_posted_vars(request.POST)

    kwargs = {}
    if 'fNom' in post and post['fNom'] != '':
        kwargs['nom__icontains'] = post['fNom']

    if 'fBailleur' in post and post['fBailleur'] != '':
        kwargs['bailleurs__in'] = [int(post['fBailleur'])]

    records, total_records, display_records = query_datatables(Projet, columns, post, **kwargs)
    results = []

    for row in records:
        edit_link = '<a href="%s">[Edit]</a>' % (reverse(editer_projet, args=[row.id]),)
        edit_link = '%s <a href="%s" class="del-link">[Suppr]</a>' % (edit_link, reverse(supprimer_projet, args=[row.id]),)
        bailleurs_list = row.bailleurs.all()
        bailleurs = ''
        if len(bailleurs_list) > 0:
            for bailleur in bailleurs_list:
                if bailleurs == '':
                    bailleurs = bailleur.nom
                else:
                    bailleurs = '%s, %s' % (bailleurs, bailleur.nom,)
        result = dict(
            nom = row.nom,
            bailleurs = bailleurs,
            actions = edit_link
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords":display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')
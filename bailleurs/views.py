# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from bailleurs.models import Bailleur
from bailleurs.forms import BailleurForm, FiltreBailleurForm
from helpers import export_excel, process_datatables_posted_vars, query_datatables
import simplejson

def lister_bailleur(request):
    if request.method == 'GET':
        form = FiltreBailleurForm()
    else:
        form = FiltreBailleurForm(request.POST)
    header_link = '<a href="%s">&raquo; Ajouter un bailleur</a>' % (reverse(ajouter_bailleur),)
    page_js = '/media/js/bailleurs/bailleurs.js'
    title = 'Liste des bailleurs'
    return render_to_response('layout_list.html', {"form": form, "title": title, "page_js": page_js, "header_link": header_link},
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
    json = simplejson.dumps([{'message': 'Enregistrement supprimé'}])
    return HttpResponse(json, mimetype='application/json')

def export_bailleur(request):
    columns = [u'Nom', u'Projets']
    dataset = Bailleur.objects.filter_for_xls(request.GET)
    response = export_excel(columns, dataset, 'bailleurs')
    return response

def ajax_bailleur(request):
    # columns titles
    columns = ['nom', 'projet', 'actions']

    # filtering
    post = process_datatables_posted_vars(request.POST)

    kwargs = {}
    if 'fNom' in post and post['fNom'] != '':
        kwargs['nom__icontains'] = post['fNom']

    if 'fProjet' in post and post['fProjet'] != '':
        kwargs['projet__icontains'] = post['fProjet']

    records, total_records, display_records = query_datatables(Bailleur, columns, post, **kwargs)
    results = []

    for row in records:
        edit_link = '<a href="%s">[Edit]</a>' % (reverse(editer_bailleur, args=[row.id]),)
        edit_link = '%s <a href="%s" class="del-link">[Suppr]</a>' % (edit_link, reverse(supprimer_bailleur, args=[row.id]),)
        result = dict(
            nom = row.nom,
            projet = row.projet,
            actions = edit_link,
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords":display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')
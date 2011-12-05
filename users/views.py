# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from helpers import export_excel, process_datatables_posted_vars, query_datatables
from django.contrib.auth.models import User
import simplejson

def lister_user(request):
    header_link = '<a href="%s">&raquo; Ajouter un utilisateur</a>' % (reverse(ajouter_projet),)
    page_js = '/media/js/users/user.js'
    title = 'Liste des utilisateurs'
    return render_to_response('layout_list_no_form.html', {"title": title, "page_js": page_js, "header_link": header_link},
                              context_instance=RequestContext(request))

def ajouter_user(request):
    if request.method == 'GET':
        form = UserForm()
        return render_to_response('users/ajouter_user.html', {'form': form, 'title': 'Ajouter un utilisateur'},
                                  context_instance=RequestContext(request))

    form = UserForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_user))
    else:
        return render_to_response('users/ajouter_user.html', {'form': form, 'title': 'Ajouter un utilisateur'},
                                  context_instance=RequestContext(request))

def editer_user(request, user_id=None):
    obj = get_object_or_404(User, pk=user_id)

    if request.method == 'GET':
        form = UserForm(instance=obj)
        return render_to_response('users/ajouter_user.html', {'form': form, 'title': 'Editer un utilisateur'},
                                  context_instance=RequestContext(request))

    form = ProjetForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_user))
    else:
        return render_to_response('users/ajouter_user.html', {'form': form, 'title': 'Editer un utilisateur'},
                                  context_instance=RequestContext(request))

def supprimer_projet(request, user_id=None):
    obj = get_object_or_404(User, pk=user_id)
    obj.delete()
    json = simplejson.dumps([{'message': 'Enregistrement supprimé'}])
    return HttpResponse(json, mimetype='application/json')

def ajax_user(request):
    # columns titles
    columns = ['nom', 'groupe', 'lastlogin', 'actions']

    # filtering
    post = process_datatables_posted_vars(request.POST)
    records = User.objects.all()
    total_records = User.objects.all().count()

    results = []

    for row in records:
        edit_link = '<a href="%s">[Edit]</a>' % (reverse(editer_user, args=[row.id]),)
        edit_link = '%s <a href="%s" class="del-link">[Suppr]</a>' % (edit_link, reverse(supprimer_user, args=[row.id]),)
        result = dict(
            nom = row.nom,
            actions = edit_link
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords":display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')
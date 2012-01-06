# -*- coding: utf-8 -*-

from datetime import datetime
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
import simplejson
from dashboard.views import index_dashboard
from helpers import process_datatables_posted_vars, query_datatables, \
    export_excel, export_pdf
from utilisateurs.forms import LoginForm, UserCreationForm, UserEditionForm,\
    UserPasswordForm

YES_NO = ('Non', 'Oui')

def login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            redirect = reverse(index_dashboard)
            if len(request.POST['next']) > 0 and request.POST['next'][:12] != 'deconnexion':
                redirect = request.POST['next']

            return HttpResponseRedirect(redirect)

    return render_to_response('utilisateurs/login.html', {'form': form},
                                      context_instance=RequestContext(request))


@login_required(login_url="/connexion")
def logout(request):
    auth.logout(request)
    return render_to_response('utilisateurs/logout.html')


@login_required(login_url="/connexion")
def add_user(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data['username'],
                                            email='',
                                            password=form.cleaned_data['password'])
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.is_active = form.cleaned_data['is_active']
            user.save()
            return HttpResponseRedirect("/utilisateurs/")

    return render_to_response("utilisateurs/register.html", {'form': form, 'title': 'Ajouter un utilisateur'},
                                                      context_instance=RequestContext(request))


@login_required(login_url="/connexion")
def edit_user(request, user_id=None):
    obj = get_object_or_404(User, pk=user_id)
    form = UserEditionForm(instance=obj)
    if request.method == 'POST':
        form = UserEditionForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(list_user))

    return render_to_response('utilisateurs/register.html', {'form': form, 'title': 'Editer un bailleur'},
                                      context_instance=RequestContext(request))


@login_required(login_url="/connexion")
def delete_user(request, user_id=None):
    obj = get_object_or_404(User, pk=user_id)
    obj.delete()
    json = simplejson.dumps([{'message': 'Enregistrement supprimé'}])
    return HttpResponse(json, mimetype='application/json')


@login_required(login_url="/connexion")
def list_user(request):
    header_link = '<a href="%s">&raquo; Ajouter un utilisateur</a>' % (reverse(add_user),)
    page_js = '/media/js/utilisateurs/utilisateurs.js'
    title = 'Liste des utilisateurs'
    return render_to_response('layout_list.html', {"title": title, "page_js": page_js, "header_link": header_link},
                                  context_instance=RequestContext(request))


def ajax_user(request):
    columns = ['username', 'name' 'actif', 'staff', 'created', 'last_login', 'actions']

    # filtering
    post = process_datatables_posted_vars(request.POST)
    kwargs = {}

    records, total_records, display_records = query_datatables(User, columns, post, **kwargs)
    results = []
    for row in records:
        edit_link = '<a href="%s">[Edit]</a>' % (reverse(edit_user, args=[row.id]),)
        edit_link = '%s <a href="%s" class="del-link">[Suppr]</a>' % (edit_link, reverse(delete_user, args=[row.id]),)
        edit_link = '%s <a href="%s">[Password]</a>' % (edit_link, reverse(set_password, args=[row.id]),)
        result = dict(
            username = row.username,
            name = "%s %s" % (row.last_name, row.first_name),
            actif = YES_NO[row.is_active],
            staff = YES_NO[row.is_staff],
            created = datetime.strftime(row.date_joined, "%d-%m-%Y %H:%M:%S"),
            last_login = datetime.strftime(row.last_login, "%d-%m-%Y %H:%M:%S"),
            actions = edit_link,
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords":display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')


@login_required(login_url="/connexion")
def set_password(request, user_id=None):
    obj = get_object_or_404(User, pk=user_id)
    form = UserPasswordForm()
    if request.method == 'POST':
        form = UserPasswordForm(request.POST, instance=obj)
        if form.is_valid():
            obj.set_password(form.cleaned_data['password'])
            obj.save()
            return HttpResponseRedirect(reverse(list_user))

    return render_to_response('utilisateurs/register.html', {'form': form, 'title': 'Changer de mot de passe'},
                                      context_instance=RequestContext(request))


@login_required(login_url="/connexion")
def export_user(request, filetype=None):
    columns = [u'Identifiant', u'Nom', u'Prénom', u'Actif', u'Admin', u'Créé le', u'Connecté le']
    users = User.objects.all()
    dataset = []
    for row in users:
        created = datetime.strftime(row.date_joined, "%d-%m-%Y %H:%M:%S"),
        last_login = datetime.strftime(row.last_login, "%d-%m-%Y %H:%M:%S"),
        row_list = [row.username, row.last_name, row.first_name,
                    YES_NO[row.is_active], YES_NO[row.is_staff], created[0], last_login[0]]
        dataset.append(row_list)

    if filetype == 'xls':
        response = export_excel(columns, dataset, 'utilisateurs')
    else:
        response = export_pdf(columns, dataset, 'utilisateurs')
    return response
# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from donnees.models import Donnees
from donnees.forms import DonneesForm, FiltreDonneesForm
from helpers import paginate, export_excel

def lister_donnees(request):
    donnees_liste = []

    if request.method == 'GET':
        form = FiltreDonneesForm()
        rows = Donnees.objects.all()
        page = int(request.GET.get('page', '1'))
    else:
        form = FiltreDonneesForm(request.POST)
        rows = Donnees.objects.filtrer(request)
        page = int(request.POST['page'])

    if rows is not None:
        for row in rows:
            donnees_id = row.id
            lien_editer = reverse(editer_donnees, args=[donnees_id])
            lien_supprimer = reverse(supprimer_donnees, args=[donnees_id])
            donnees = dict(
                id=row.id,
                nom=row.nom,
                lien_editer=lien_editer,
                lien_supprimer=lien_supprimer
            )
            donnees_liste.append(donnees)

    donnees = paginate(donnees_liste, 25, page)

    return render_to_response('donnees/lister_donnees.html', {"donnees": donnees, "form": form},
                              context_instance=RequestContext(request))

def ajouter_donnees(request):
    if request.method == 'GET':
        form = DonneesForm()
        return render_to_response('donnees/ajouter_donnees.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = DonneesForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_donnees))
    else:
        return render_to_response('donnees/ajouter_donnees.html', {'form': form},
                                  context_instance=RequestContext(request))

def editer_donnees(request, donnees_id=None):
    obj = get_object_or_404(Donnee, pk=donnees_id)

    if request.method == 'GET':
        form = DonneesForm(instance=obj)
        return render_to_response('donnees/ajouter_donnees.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = DonneesForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_donnees))
    else:
        return render_to_response('donnees/ajouter_donnees.html', {'form': form},
                                  context_instance=RequestContext(request))

def supprimer_donnees(request, donnees_id=None):
    obj = get_object_or_404(Donnee, pk=donnees_id)
    obj.delete()
    return HttpResponseRedirect(reverse(lister_donnees))
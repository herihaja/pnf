# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from donnees.models import Donnees, Cumul
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
        if request.POST['action'] == 'export':
            return _export(rows)

    if rows is not None:
        for row in rows:
            donnee_id = row.id
            lien_editer = reverse(editer_donnees, args=[donnee_id])
            lien_supprimer = reverse(supprimer_donnees, args=[donnee_id])
            donnees = dict(
                id=row.id,
                code = row.commune.code,
                periode = row.periode,
                demandes = row.demandes,
                oppositions = row.oppositions,
                resolues = row.resolues,
                certificats = row.certificats,
                femmes = row.femmes,
                surfaces = row.surfaces,
                recettes = row.recettes,
                garanties = row.garanties,
                reconnaissances = row.reconnaissances,
                mutations = row.mutations,
                valide = row.valide,
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
        if form.save():
            form = RegionForm()
            message = "Vos données ont été ajoutées avec succès."
        else:
            message = "Veuillez d'abord enregistrer les données des mois précédents."
        return render_to_response('donnees/ajouter_donnees.html', {'form': form, 'message': message},
                                  context_instance=RequestContext(request))
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
            form = RegionForm()
            message = "Vos données ont été mises à jour avec succès."
        else:
            message = "Veuillez d'abord enregistrer les données des mois précédents."
        return render_to_response('donnees/ajouter_donnees.html', {'form': form, 'message': message},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('donnees/ajouter_donnees.html', {'form': form},
                                  context_instance=RequestContext(request))

def supprimer_donnees(request, donnee_id=None):
    obj = get_object_or_404(Donnees, pk=donnee_id)
    if obj.delete():
        message = "Vos données on été supprimées avec succès."
    else:
        message = "Vous devez supprimer les données des mois suivants avant de poursuivre."
    return HttpResponseRedirect(reverse(lister_donnees))



def lister_cumuls(request):
    cumuls_liste = []

    if request.method == 'GET':
        form = FiltreDonneesForm()
        rows = Cumul.objects.all()
        page = int(request.GET.get('page', '1'))
    else:
        form = FiltreDonneesForm(request.POST)
        rows = Cumul.filtered_objects.filtrer(request)
        page = int(request.POST['page'])
        if request.POST['action'] == 'export':
            return _export(rows)

    if rows is not None:
        for row in rows:
            cumuls = dict(
                code = row.commune.code,
                periode = row.periode,
                demandes = row.demandes,
                oppositions = row.oppositions,
                resolues = row.resolues,
                certificats = row.certificats,
                femmes = row.femmes,
                surfaces = row.surfaces,
                recettes = row.recettes,
                garanties = row.garanties,
                reconnaissances = row.reconnaissances,
                mutations = row.mutations,
            )
            cumuls_liste.append(cumuls)

    cumuls = paginate(cumuls_liste, 25, page)

    return render_to_response('donnees/lister_cumul.html', {"cumuls": cumuls, "form": form},
                              context_instance=RequestContext(request))

def _export(rows):
    header = ['Commune', 'Sms','Periode', 'Demandes', 'Oppositions', 'Resolues', 'Certificats', 'Femmes', 'Recettes', 'Mutations', 'Surfaces', 'Garanties', 'Reconnaissance', 'Valide']
    liste = []
    for row in rows:
        cleaned_row = [row.commune.nom, row.sms.message, row.periode, row.demandes, row.oppositions, row.resolues, row.certificats, row.femmes, row.recettes, row.mutations, row.surfaces, row.garanties, row.reconnaissances, row.valide]
        liste.append(cleaned_row)
    ret = export_excel(header, liste, 'données')
    return ret

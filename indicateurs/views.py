# -*- coding: utf-8 -*-
from __future__ import division
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from donnees.models import Donnees, Cumul
from helpers import paginate, export_excel
from indicateurs.forms import FiltreIndicateursForm, FiltreIndicateurForm, FiltreRatioForm

def indicateurs_par_date(request):
    donnees_liste = []

    if request.method == 'GET':
        form = FiltreIndicateursForm()
        rows = Donnees.objects.filter(valide=True).order_by('commune', 'periode')
        page = int(request.GET.get('page', '1'))
    else:
        form = FiltreIndicateursForm(request.POST)
        rows = Donnees.objects.filtrer(request).order_by('commune', 'periode')
        page = int(request.POST['page'])
        if request.POST['action'] == 'export':
            return _export(rows)

    if rows is not None:
        for row in rows:
            donnees = dict(
                id=row.id,
                code = row.commune.code,
                commune = row.commune.nom,
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
            donnees_liste.append(donnees)

    donnees = paginate(donnees_liste, 25, page)
    return render_to_response('indicateurs/lister_indicateurs.html', {"donnees": donnees, "form": form},
                              context_instance=RequestContext(request))

def indicateur_par_date(request):
    donnees_liste = []
    indicateur = 'demandes'
    if request.method == 'GET':
        form = FiltreIndicateurForm()
        rows = Donnees.objects.filter(valide=True).values('commune', 'commune__nom', 'periode', indicateur).order_by('commune', 'periode')
        page = int(request.GET.get('page', '1'))
    else:
        form = FiltreIndicateurForm(request.POST)
        indicateur = request.POST['indicateur']
        rows = Donnees.objects.filtrer(request).values('commune', 'commune__nom', 'periode', indicateur).order_by('commune', 'periode')
        page = int(request.POST['page'])
        if request.POST['action'] == 'export':
            return _export(rows)

    if rows is not None:
        commune = None
        mois = 1
        donnees = {}
        total = 0
        for row in rows:
            # nouvelle ligne
            if row['commune'] != commune:
                # enregistrer la ligne
                if commune is not None:
                    # remplir les colonnes à 12 si nécessaire
                    while mois <= 12:
                        donnees[mois] = '-'
                        mois += 1
                    donnees['total'] = total
                    donnees_liste.append(donnees)
                    # reinitialiser les compteurs
                    mois = 1
                    donnees = {}
                    total = 0
                commune = row['commune']
                donnees['commune'] = row['commune__nom']
            while mois < row['periode'].month:
                donnees[mois] = '-'
                mois += 1
            donnees[mois] = row[indicateur]
            total += row[indicateur]
            mois += 1

    donnees = paginate(donnees_liste, 25, page)
    return render_to_response('indicateurs/lister_indicateur.html', {"donnees": donnees, "form": form},
                              context_instance=RequestContext(request))

def ratio(request, numerateur, denominateur):
    donnees_liste = []
    if request.method == 'GET':
        form = FiltreRatioForm()
        rows = Cumul.objects.all().values('commune', 'commune__nom', 'periode', numerateur, denominateur).order_by('commune', 'periode')
        page = int(request.GET.get('page', '1'))
    else:
        form = FiltreRatioForm(request.POST)
        rows = Cumul.filtered_objects.filtrer(request).values('commune', 'commune__nom', 'periode', numerateur, denominateur).order_by('commune', 'periode')
        page = int(request.POST['page'])
        if request.POST['action'] == 'export':
            return _export(rows)

    if rows is not None:
        commune = None
        mois = 1
        donnees = {}
        total = 0
        n = 0
        for row in rows:
            # nouvelle ligne
            if row['commune'] != commune:
                # enregistrer la ligne
                if commune is not None:
                    # remplir les colonnes à 12 si nécessaire
                    while mois <= 12:
                        donnees[mois] = '-'
                        mois += 1
                    if n > 0:
                        donnees['moyenne'] = '%.2f' % (total / n)
                    else:
                        donnees['moyenne'] = '-'
                    donnees_liste.append(donnees)
                    # reinitialiser les compteurs
                    mois = 1
                    donnees = {}
                    total = 0
                    n = 0
                commune = row['commune']
                donnees['commune'] = row['commune__nom']
            while mois < row['periode'].month:
                donnees[mois] = '-'
                mois += 1
            if row[denominateur] != 0:
                ratio = row[numerateur] / row[denominateur]
                total += ratio
                donnees[mois] = '%.2f' % ratio
                n += 1
            else:
                donnees[mois] = '-'

            mois += 1
        # completer la derniere ligne
        if len(rows) > 0:
            # remplir les colonnes à 12 si nécessaire
            while mois <= 12:
                donnees[mois] = '-'
                mois += 1
            if n > 0:
                donnees['moyenne'] = '%.2f' % (total / n)
            else:
                donnees['moyenne'] = '-'
            donnees_liste.append(donnees)

    donnees = paginate(donnees_liste, 25, page)
    return render_to_response('indicateurs/lister_ratio.html', {"donnees": donnees, "form": form},
                              context_instance=RequestContext(request))
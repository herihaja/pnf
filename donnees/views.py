# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from donnees.models import Donnees, Cumul, Recu
from donnees.forms import DonneesForm, FiltreDonneesForm
from helpers import export_excel, process_datatables_posted_vars, create_compare_condition, query_datatables
import simplejson
from datetime import datetime
from localites.forms import FiltreCommuneForm

def lister_donnees(request):
    if request.method == 'GET':
        form = FiltreDonneesForm()
    else:
        form = FiltreDonneesForm(request.POST)
    header_link = '<a href="%s">&raquo; Insertion manuelle</a>' % (reverse(ajouter_donnees),)
    page_js = '/media/js/donnees/donnees.js'
    title = 'Liste des données'
    return render_to_response('layout_list.html', {"form": form, "title": title, "page_js": page_js, "header_link": header_link},
                              context_instance=RequestContext(request))

def ajax_donnees(request):
    # columns titles
    columns = ['commune', 'code', 'periode', 'demandes', 'oppositions', 'resolues', 'certificats', 'femmes', 'surfaces', 'recettes', 'garanties', 'reconnaissances', 'mutations', 'valide', 'actions']

    # filtering
    post = process_datatables_posted_vars(request.POST)
    kwargs = {}

    if 'fCommune' in post and post['fCommune'] != '':
        kwargs['commune'] = str(post['fCommune'])
    else:
        if 'fCode' in post and post['fCode'] != '':
            kwargs['commune__code__icontains'] = post['fCode']
        if 'fDistrict' in post and post['fDistrict'] != '':
            kwargs['commune__district'] = post['fDistrict']
        else:
            if 'fRegion' in post and post['fRegion'] != '':
                kwargs['commune__district__region'] = post['fRegion']

    # filtering of indicateurs
    for i in range(3, 12):
        post_key = 'f%s' % (columns[i].capitalize(),)
        if post_key in post and post[post_key] != '':
            key, value = create_compare_condition(columns[i], post[post_key])
            kwargs[key] = value
            
    if 'fPeriodeDe' in post and post['fPeriodeDe'] != '':
        cree_de = datetime.strptime(post['fPeriodeDe'], "%d/%m/%Y")
        cree_de = datetime.strftime(cree_de, "%Y-%m-%d")
        kwargs['periode__gte'] = cree_de
    if 'fPeriodeA' in post and post['fPeriodeA'] != '':
        cree_a = datetime.strptime(post['fPeriodeA'], "%d/%m/%Y")
        cree_a = datetime.strftime(cree_a, "%Y-%m-%d")
        kwargs['periode__lte'] = cree_a

    records, total_records, display_records = query_datatables(Donnees, columns, post, **kwargs)
    results = []
    for row in records:
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

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords": display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')

def ajouter_donnees(request):
    if request.method == 'GET':
        form = DonneesForm(region_id=1, initial={'region': 1,})
        return render_to_response('donnees/ajouter_donnees.html', {'form': form, 'title': u'Ajout manuel'},
                                  context_instance=RequestContext(request))

    form = DonneesForm(request.POST)
    if form.is_valid():
        if form.save():
            message = "Vos données ont été ajoutées avec succès."
            return HttpResponseRedirect(reverse(lister_donnees))
        return render_to_response('donnees/ajouter_donnees.html', {'form': form, 'message': message, 'title': u'Ajout manuel'},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('donnees/ajouter_donnees.html', {'form': form, 'title': u'Ajout manuel'},
                                  context_instance=RequestContext(request))

def editer_donnees(request, donnee_id=None):
    obj = get_object_or_404(Donnees, pk=donnee_id)

    if request.method == 'GET':
        region_id = obj.commune.district.region_id
        district_id = obj.commune.district_id
        form = DonneesForm(instance=obj, region_id=region_id, district_id=district_id,
                           initial={'commune': obj.commune_id, 'district': district_id, 'region': region_id,})
        return render_to_response('donnees/ajouter_donnees.html', {'form': form, 'title': u'Edition'},
                                  context_instance=RequestContext(request))

    form = DonneesForm(request.POST, instance=obj)
    if form.is_valid():
        if form.save():
            message = "Vos données ont été mises à jour avec succès."
            return HttpResponseRedirect(reverse(lister_donnees))
        return render_to_response('donnees/ajouter_donnees.html', {'form': form, 'message': message, 'title': u'Edition'},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('donnees/ajouter_donnees.html', {'form': form},
                                  context_instance=RequestContext(request))

def supprimer_donnees(request, donnee_id=None):
    obj = get_object_or_404(Donnees, pk=donnee_id)
    obj.delete()
    json = simplejson.dumps([{'message': 'Enregistrement supprimé'}])
    return HttpResponse(json, mimetype='application/json')

def export_donnees(request):
    columns = [u'Commune', u'Code', u'Période', u'Demandes', u'Oppositions', u'Résolues', u'Certificats', u'Femmes', u'Surfaces', u'Recettes', u'Garanties', u'Reconnaissances', u'Mutations', u'Validé']
    dataset = Donnees.objects.filter_for_xls(request.GET)
    response = export_excel(columns, dataset, 'donnees')
    return response

def lister_cumuls(request):
    if request.method == 'GET':
            form = FiltreDonneesForm()
    else:
        form = FiltreDonneesForm(request.POST)
    title = 'Données cumulées'
    page_js = '/media/js/donnees/cumuls.js'
    return render_to_response('layout_list.html', {"form": form, "title": title, "page_js": page_js},
                              context_instance=RequestContext(request))

def ajax_cumuls(request):
    # columns titles
    columns = ['commune', 'code', 'periode', 'demandes', 'oppositions', 'resolues', 'certificats', 'femmes', 'surfaces', 'recettes', 'garanties', 'reconnaissances', 'mutations']

    # filtering
    post = process_datatables_posted_vars(request.POST)
    kwargs = {}

    if 'fCommune' in post and post['fCommune'] != '':
        kwargs['commune'] = str(post['fCommune'])
    else:
        if 'fCode' in post and post['fCode'] != '':
            kwargs['commune__code__icontains'] = post['fCode']
        if 'fDistrict' in post and post['fDistrict'] != '':
            kwargs['commune__district'] = post['fDistrict']
        else:
            if 'fRegion' in post and post['fRegion'] != '':
                kwargs['commune__district__region'] = post['fRegion']

    # filtering of indicateurs
    for i in range(3, 12):
        post_key = 'f%s' % (columns[i].capitalize(),)
        if post_key in post and post[post_key] != '':
            key, value = create_compare_condition(columns[i], post[post_key])
            kwargs[key] = value

    if 'fPeriodeDe' in post and post['fPeriodeDe'] != '':
        cree_de = datetime.strptime(post['fPeriodeDe'], "%d/%m/%Y")
        cree_de = datetime.strftime(cree_de, "%Y-%m-%d")
        kwargs['periode__gte'] = cree_de
    if 'fPeriodeA' in post and post['fPeriodeA'] != '':
        cree_a = datetime.strptime(post['fPeriodeA'], "%d/%m/%Y")
        cree_a = datetime.strftime(cree_a, "%Y-%m-%d")
        kwargs['periode__lte'] = cree_a

    records, total_records, display_records = query_datatables(Cumul, columns, post, **kwargs)
    results = []

    for row in records:
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
            mutations = row.mutations,
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords":display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')

def export_cumuls(request):
    columns = [u'Commune', u'Code', u'Période', u'Demandes', u'Oppositions', u'Résolues', u'Certificats', u'Femmes', u'Surfaces', u'Recettes', u'Garanties', u'Reconnaissances', u'Mutations']
    dataset = Cumul.objects.filter_for_xls(request.GET)
    response = export_excel(columns, dataset, 'cumul')
    return response

def lister_recu(request):
    title = 'Données reçues'
    page_js = '/media/js/donnees/recu.js'
    return render_to_response('layout_list_no_form.html', {"title": title, "page_js": page_js},
                              context_instance=RequestContext(request))

def supprimer_recu(request, recu_id=None):
    obj = get_object_or_404(Recu, pk=recu_id)
    obj.delete()
    json = simplejson.dumps([{'message': 'Enregistrement supprimé'}])
    return HttpResponse(json, mimetype='application/json')

def tester_recu(request, recu_id=None):
    obj = get_object_or_404(Recu, pk=recu_id)

    # prendre les dernieres donnees cumulees du guichet (commune)
    cumul_demandes = 0
    cumul_certificats = 0
    cumul_reco = 0
    cumul = Cumul.objects.filter(commune=obj.commune, periode__lt=obj.periode).values('certificats', 'demandes', 'reconnaissances').order_by('-periode')[:1]
    if len(cumul) == 1:
        cumul_demandes = cumul[0]['demandes']
        cumul_certificats = cumul[0]['certificats']
        cumul_reco = cumul[0]['reconnaissances']


    if request.method == 'GET':
        region_id = obj.commune.district.region_id
        district_id = obj.commune.district_id
        form = DonneesForm(instance=obj, region_id=region_id, district_id=district_id,
                           initial={'commune': obj.commune_id, 'district': district_id, 'region': region_id,})
        return render_to_response('donnees/tester_recu.html', {'form': form, 'title': u'Tests de cohérence', 'id': obj.id,
                                                               'demandes': cumul_demandes, 'recos': cumul_reco, 'certifs': cumul_certificats,},
                                  context_instance=RequestContext(request))

def valider_recu(request, recu_id=None):
    obj = get_object_or_404(Recu, pk=recu_id)

    donnees = Donnees(
        commune = obj.commune,
        sms = obj.sms,
        periode = obj.periode,
        demandes = int(request.POST['demandes']),
        oppositions = int(request.POST['oppositions']),
        resolues = int(request.POST['resolues']),
        certificats = int(request.POST['certificats']),
        femmes = int(request.POST['femmes']),
        surfaces = float(request.POST['surfaces']),
        recettes = int(request.POST['recettes']),
        garanties = int(request.POST['garanties']),
        reconnaissances = int(request.POST['reconnaissances']),
        valide = True,
        mutations = int(request.POST['mutations']),
    )
    
    if donnees.save():
        obj.delete()
        message = u'Enregistrement validé'

    json = simplejson.dumps([{'message': message}])
    return HttpResponse(json, mimetype='application/json')

def ajax_recu(request):
    post = process_datatables_posted_vars(request.POST)
    
    records = Recu.objects.all().order_by('-ajout')
    total_records = len(records)
    display_records = total_records
    results = []

    for row in records:
        edit_link = '<a href="%s">[Tester]</a>' % (reverse(tester_recu, args=[row.id]),)
        edit_link = '%s <a href="%s" class="del-link">[Suppr]</a>' % (edit_link, reverse(supprimer_recu, args=[row.id]),)
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
            mutations = row.mutations,
            actions = edit_link,
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords": display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')

def exporter_pour_site(request):
    if request.method == 'GET':
        form = FiltreDonneesForm()
    else:
        form = FiltreDonneesForm(request.POST)
    page_js = '/media/js/donnees/export.js'
    title = 'Export site'
    return render_to_response('layout_list.html', {"form": form, "title": title, "page_js": page_js},
                              context_instance=RequestContext(request))

def export_site(request):
    columns = [u'ID_COMMUNE', u'ANNEE', u'MOIS', u'REGION', u'DISTRICT', u'COMMUNES', u'BAILLEUR',
               u'NB_DEMANDE', u'NB_DEM_REJ', u'NB_CF_DELI', u'NB_CF_FEMM', u'NB_BENEFIC', u'NB_BENEF_F',
               u'SUPERFICIE', u'NB_OPPOSIT', u'NB_OPP_RES', u'RECETTE']
    dataset = Donnees.objects.filter_for_site(request.GET)
    response = export_excel(columns, dataset, 'export')
    return response
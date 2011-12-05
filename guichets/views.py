# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from guichets.models import Guichet, Rma
from guichets.forms import GuichetForm, FiltreGuichetForm, FiltreBailleurForm, FiltreRmaForm
from helpers import process_datatables_posted_vars, export_excel, query_datatables, export_pdf
import simplejson

def lister_guichet(request):
    if request.method == 'GET':
        form = FiltreGuichetForm()
    else:
        form = FiltreGuichetForm(request.POST)
    header_link = '<a href="%s">&raquo; Ajouter un guichet</a>' % (reverse(ajouter_guichet),)
    page_js = '/media/js/guichets/guichets.js'
    title = 'Liste des guichets'
    return render_to_response('layout_list.html', {"form": form, "title": title, "page_js": page_js, "header_link": header_link},
                              context_instance=RequestContext(request))

def lister_bailleurs(request):
    if request.method == 'GET':
        form = FiltreBailleurForm()
    else:
        form = FiltreBailleurForm(request.POST)
    page_js = '/media/js/guichets/bailleurs.js'
    title = 'Liste des guichets par bailleurs'
    return render_to_response('layout_list.html', {"form": form, "title": title, "page_js": page_js},
                              context_instance=RequestContext(request))

def ajouter_guichet(request):
    if request.method == 'GET':
        form = GuichetForm(region_id=1, initial={'region': 1,})
        return render_to_response('guichets/ajouter_guichet.html', {'form': form, 'title': 'Ajouter un guichet'},
                                  context_instance=RequestContext(request))

    form = GuichetForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_guichet))
    else:
        return render_to_response('guichets/ajouter_guichet.html', {'form': form, 'title': 'Ajouter un guichet'},
                                  context_instance=RequestContext(request))

def editer_guichet(request, guichet_id=None):
    obj = get_object_or_404(Guichet, pk=guichet_id)

    if request.method == 'GET':
        region_id = obj.commune.district.region_id
        district_id = obj.commune.district_id
        form = GuichetForm(instance=obj, region_id=region_id, district_id=district_id,
                           initial={'commune': obj.commune_id, 'district': district_id, 'region': region_id,})
        return render_to_response('guichets/ajouter_guichet.html', {'form': form, 'title': 'Editer un guichet'},
                                  context_instance=RequestContext(request))

    form = GuichetForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_guichet))
    else:
        return render_to_response('guichets/ajouter_guichet.html', {'form': form, 'title': 'Editer un guichet'},
                                  context_instance=RequestContext(request))

def supprimer_guichet(request, guichet_id=None):
    obj = get_object_or_404(Guichet, pk=guichet_id)
    obj.delete()
    json = simplejson.dumps([{'message': 'Enregistrement supprimé'}])
    return HttpResponse(json, mimetype='application/json')

def ajax_guichet(request):
    # columns titles
    columns = ['commune', 'code', 'creation', 'agf1', 'num1', 'password1', 'agf2', 'num2', 'password2', 'etat', 'actions']

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
    if 'fAgf1' in post and post['fAgf1'] != '':
        kwargs['agf1__icontains'] = str(post['fAgf1'])
    if 'fMobile1' in post and post['fMobile1'] != '':
        kwargs['mobile1__icontains'] = str(post['fMobile1'])
    if 'fAgf2' in post and post['fAgf2'] != '':
        kwargs['agf2__icontains'] = str(post['fAgf2'])
    if 'fMobile2' in post and post['fMobile2'] != '':
        kwargs['mobile2__icontains'] = str(post['fMobile2'])
    if 'fCreede' in post and post['fCreede'] != '':
        cree_de = datetime.strptime(post['fCreede'], "%d/%m/%Y")
        cree_de = datetime.strftime(cree_de, "%Y-%m-%d")
        kwargs['creation__gte'] = cree_de
    if 'fCreea' in post and post['fCreea'] != '':
        cree_a = datetime.strptime(post['fCreea'], "%d/%m/%Y")
        cree_a = datetime.strftime(cree_a, "%Y-%m-%d")
        kwargs['creation__lte'] = cree_a
    if 'fEtat' in post and post['fEtat'] != '':
        kwargs['etat'] = post['fEtat']

    records, total_records, display_records = query_datatables(Guichet, columns, post, **kwargs)
    results = []
    for row in records:
        edit_link = '<a href="%s">[Edit]</a>' % (reverse(editer_guichet, args=[row.id]),)
        edit_link = '%s <a href="%s" class="del-link">[Suppr]</a>' % (edit_link, reverse(supprimer_guichet, args=[row.id]),)
        if row.password1 is not None and len(row.password1) > 0:
            password1 = 'Oui'
        else:
            password1 = 'Non'
        if row.agf2 is not None:
            if row.password2 is not None and len(row.password2) > 0:
                password2 = 'Oui'
            else:
                password2 = 'Non'
        else:
            password2 = ''

        if row.creation is not None:
            creation = datetime.strftime(row.creation, "%d/%m/%Y")
        else:
            creation = ''

        result = dict(
            commune = row.commune.nom,
            code = row.commune.code,
            creation = creation,
            agf1 = row.agf1,
            num1 = row.mobile1,
            password1 = password1,
            agf2 = row.agf2,
            num2 = row.mobile2,
            password2 = password2,
            etat = row.get_etat_display(),
            actions = edit_link,
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords":display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')

def ajax_bailleur(request):
    # columns titles
    columns = ['commune', 'code', 'creation', 'bailleurs', 'projets', 'etat']

    # filtering
    post = process_datatables_posted_vars(request.POST)

    kwargs = {}
    if 'fPeriode' in post and post['fPeriode'] != '':
        periode = datetime.strptime(post['fPeriode'], "%d/%m/%Y")
    else:
        periode = datetime.now()
    kwargs['periode__year='] = periode.year
    kwargs['periode__month='] = periode.month

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
    if 'fCreede' in post and post['fCreede'] != '':
        cree_de = datetime.strptime(post['fCreede'], "%d/%m/%Y")
        cree_de = datetime.strftime(cree_de, "%Y-%m-%d")
        kwargs['creation__gte'] = cree_de
    if 'fCreea' in post and post['fCreea'] != '':
        cree_a = datetime.strptime(post['fCreea'], "%d/%m/%Y")
        cree_a = datetime.strftime(cree_a, "%Y-%m-%d")
        kwargs['creation__lte'] = cree_a
    if 'fEtat' in post and post['fEtat'] != '':
        kwargs['etat'] = post['fEtat']
    if 'fProjet' in post and post['fProjet'] != '':
        kwargs['projets__in'] = [int(post['fProjet'])]
    else:
        if 'fBailleur' in post and post['fBailleur'] != '':
            kwargs['bailleurs__in'] = [int(post['fBailleur'])]

    records, total_records, display_records = query_datatables(Guichet, columns, post, **kwargs)
    results = []
    for row in records:
        bailleurs_list = row.bailleurs.all()
        bailleurs = ''
        if len(bailleurs_list) > 0:
            for bailleur in bailleurs_list:
                if bailleurs == '':
                    bailleurs = bailleur.nom
                else:
                    bailleurs = '%s, %s' % (bailleurs, bailleur.nom,)

        projets_list = row.projets.all()
        projets = ''
        if len(projets_list) > 0:
            for projet in projets_list:
                if projets == '':
                    projets = projet.nom
                else:
                    projets = '%s, %s' % (projets, projet.nom,)

        if row.creation is not None:
            creation = datetime.strftime(row.creation, "%d-%m-%Y")
        else:
            creation = ''

        result = dict(
            commune = row.commune.nom,
            code = row.commune.code,
            creation = creation,
            bailleurs = bailleurs,
            projets = projets,
            etat = row.get_etat_display(),
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords":display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')

def export_guichet(request, filetype=None):
    columns = [u'Commune', u'Code', u'Creation', u'Agf1', u'Mobile1', 'Password1', u'Agf2', u'Mobile2', 'Password2', u'Etat']
    dataset = Guichet.objects.filter_for_xls(request.GET)
    if filetype == 'xls':
        response = export_excel(columns, dataset, 'guichets')
    else:
        response = export_pdf(columns, dataset, 'guichets')
    return response

def export_guichet_bailleurs(request, filetype=None):
    columns = [u'Commune', u'Code', u'Création', u'Guichets', u'Bailleurs', u'Projets']
    dataset = Guichet.objects.filter_projets_for_xls(request.GET)
    if filetype == 'xls':
        response = export_excel(columns, dataset, 'guichets')
    else:
        response = export_pdf(columns, dataset, 'guichets', 1)
    return response

def lister_envoi_rma(request):
    if request.method == 'GET':
        form = FiltreRmaForm()
    else:
        form = FiltreRmaForm(request.POST)

    page_js = '/media/js/guichets/rma.js'
    title = 'RMA envoyés'
    return render_to_response('layout_list.html', {"form": form, "title": title, "page_js": page_js},
                              context_instance=RequestContext(request))


def _create_condition_for_envoi_rma(post):
    kwargs = {}
    periode = datetime.now() - timedelta(weeks=4)
    if 'fCommune' in post and post['fCommune'] != '':
        kwargs['guichet__commune'] = str(post['fCommune'])
    else:
        if 'fDistrict' in post and post['fDistrict'] != '':
            kwargs['guichet__commune__district'] = post['fDistrict']
        else:
            if 'fRegion' in post and post['fRegion'] != '':
                kwargs['guichet__commune__district__region'] = post['fRegion']
    if 'fAgf' in post and post['fAgf'] != '':
        kwargs['agf__icontains'] = str(post['fAgf'])
    if 'fStatut' in post and post['fStatut'] != '':
        kwargs['sms__statut'] = post['fStatut']
    if 'fPeriode' in post and post['fPeriode'] != '':
        periode = "01/%s" % (post['fPeriode'],)
        periode = datetime.strptime(periode, "%d/%m/%Y")

    kwargs['periode__year'] = periode.year
    kwargs['periode__month'] = periode.month

    return kwargs

def ajax_envoi_rma(request):
    # columns titles
    columns = ['guichet__commune__district__region', 'guichet__commune__district',
               'guichet__commune', 'sms__date_reception', 'sms__statut', 'agf']

    # filtering
    post = process_datatables_posted_vars(request.POST)
    kwargs = _create_condition_for_envoi_rma(post)
    records, total_records, display_records = query_datatables(Rma, columns, post, **kwargs)
    results = []
    for row in records:
        result = dict(
            region = row.guichet.commune.district.region.nom,
            district = row.guichet.commune.district.nom,
            commune = row.guichet.commune.nom,
            reception = datetime.strftime(row.sms.date_reception, "%d-%m-%Y %H:%M:%S"),
            statut = row.sms.get_statut_display(),
            agf = row.agf,
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords":display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')

def export_envoi_rma(request, filetype=None):
    columns = [u'Region', u'District', u'Commune', u'Reception', u'Statut', 'Agf']

    post = process_datatables_posted_vars(request.POST)
    kwargs = _create_condition_for_envoi_rma(post)
    records = Rma.objects.filter(**kwargs)

    dataset = []
    for row in records:
        reception = datetime.strftime(row.sms.date_reception, "%d-%m-%Y %H:%M:%S")
        row_list = [row.guichet.commune.district.region.nom,
                    row.guichet.commune.district.nom,
                    row.guichet.commune.nom,
                    reception, row.sms.get_statut_display(), row.agf]
        dataset.append(row_list)

    if filetype == 'xls':
        response = export_excel(columns, dataset, 'rma-envoi')
    else:
        response = export_pdf(columns, dataset, 'rma-envoi')
    return response
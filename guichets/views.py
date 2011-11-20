# -*- coding: utf-8 -*-

from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from guichets.models import Guichet
from guichets.forms import GuichetForm, FiltreGuichetForm, FiltreBailleurForm
from helpers import process_datatables_posted_vars, export_excel, query_datatables
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
    title = 'Liste des guichets'
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

def export(rows):
    header = ['Commune', 'Agf1',  'Mobile1', 'Password1', 'Agf2', 'Mobile2', 'Password2', 'Etat']
    liste = []
    for row in rows:
        cleaned_row = [row.commune.code, row.agf1, row.mobile1, row.agf2, row.mobile2, row.etat]
        liste.append(cleaned_row)
    ret = export_excel(header, liste, 'guichets')
    return ret

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
    columns = ['commune', 'code', 'creation', 'bailleurs', 'etat']

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
    if 'fBailleur' in post and post['fBailleur'] != '':
        kwargs['bailleurs__in'] = post['fBailleur']

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

        result = dict(
            commune = row.commune.nom,
            code = row.commune.code,
            creation = datetime.strftime(row.creation, "%d-%m-%Y"),
            bailleurs = bailleurs,
            etat = row.get_etat_display(),
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords":display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')

def export_guichet(request):
    columns = [u'Commune', u'Code', u'Creation', u'Agf1', u'Mobile1', 'Password1', u'Agf2', u'Mobile2', 'Password2', u'Etat']
    dataset = Guichet.objects.filter_for_xls(request.GET)
    response = export_excel(columns, dataset, 'guichets')
    return response

def export_guichet_bailleurs(request):
    columns = [u'Commune', u'Code', u'Création', u'Guichets']
    dataset = Guichet.objects.filter_bailleurs_for_xls(request.GET)
    response = export_excel(columns, dataset, 'guichets')
    return response
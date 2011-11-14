# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from guichets.views import editer_guichet
from localites.models import Province, Region, District, Commune
from localites.forms import ProvinceForm, RegionForm, DistrictForm, CommuneForm, FiltreDistrictForm, FiltreCommuneForm
from helpers import process_datatables_posted_vars, query_datatables, export_excel
import simplejson

def ajouter_province(request):
    if request.method == 'GET':
        form = ProvinceForm()
        return render_to_response('localites/ajouter_province.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = ProvinceForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_localite))
    else:
        return render_to_response('localites/ajouter_province.html', {'form': form},
                                  context_instance=RequestContext(request))

def editer_province(request, province_id=None):
    return HttpResponseRedirect(reverse(lister_province))

def supprimer_province(request, province_id=None):
    obj = get_object_or_404(Province, pk=province_id)
    obj.delete()
    return HttpResponseRedirect(reverse(lister_province))

def lister_region(request):
    header_link = '<a href="%s">&raquo; Ajouter une région</a>' % (reverse(ajouter_region),)
    page_js = '/media/js/localites/regions.js'
    title = 'Liste des régions'
    return render_to_response('layout_list.html', {"title": title, "page_js": page_js, "header_link": header_link},
                              context_instance=RequestContext(request))

def ajax_region(request):
    regions = Region.objects.all()
    total_records = display_records = Region.objects.all().count()

    results = []
    for row in regions:
        edit_link = '<a href="%s">[Edit]</a>' % (reverse(editer_region, args=[row.id]),)
        edit_link = '%s <a href="%s" class="del-link">[Suppr]</a>' % (edit_link, reverse(supprimer_region, args=[row.id]),)
        result = dict(
            nom = row.nom,
            code = row.code,
            actions = edit_link,
        )
        results.append(result)

    results = {"iTotalRecords": total_records, "iTotalDisplayRecords": display_records, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')

def ajouter_region(request):
    if request.method == 'GET':
        form = RegionForm()
        return render_to_response('localites/ajouter_region.html', {'form': form, 'title': 'Ajouter une région'},
                                  context_instance=RequestContext(request))

    form = RegionForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_region))
    else:
        return render_to_response('localites/ajouter_region.html', {'form': form, 'title': 'Ajouter une région'},
                                  context_instance=RequestContext(request))

def editer_region(request, region_id=None):
    obj = get_object_or_404(Region, pk=region_id)

    if request.method == 'GET':
        form = RegionForm(instance=obj)
        return render_to_response('localites/ajouter_region.html', {'form': form, 'title': 'Editer une région'},
                                  context_instance=RequestContext(request))

    form = RegionForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_region))
    else:
        return render_to_response('localites/ajouter_region.html', {'form': form, 'title': 'Editer une région'},
                                  context_instance=RequestContext(request))

def supprimer_region(request, region_id=None):
    obj = get_object_or_404(Region, pk=region_id)
    obj.delete()
    # return HttpResponseRedirect(reverse(lister_region))
    json = simplejson.dumps([{'message': 'Enregistrement supprimé'}])
    return HttpResponse(json, mimetype='application/json')

def export_region(request):
    columns = [u'Region', u'Code']
    dataset = Region.objects.filter_for_xls()
    response = export_excel(columns, dataset, 'regions')
    return response

def lister_district(request):
    if request.method == 'GET':
        form = FiltreDistrictForm()
    else:
        form = FiltreDistrictForm(request.POST)
    header_link = '<a href="%s">&raquo; Ajouter un district</a>' % (reverse(ajouter_district),)
    page_js = '/media/js/localites/districts.js'
    title = 'Liste des districts'
    return render_to_response('layout_list.html', {"form": form, "title": title, "page_js": page_js, "header_link": header_link},
                              context_instance=RequestContext(request))

def ajouter_district(request):
    if request.method == 'GET':
        form = DistrictForm()
        return render_to_response('localites/ajouter_district.html', {'form': form, 'title': 'Ajouter un district'},
                                  context_instance=RequestContext(request))

    form = DistrictForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_district))
    else:
        return render_to_response('localites/ajouter_district.html', {'form': form, 'title': 'Ajouter un district'},
                                  context_instance=RequestContext(request))

def editer_district(request, district_id=None):
    obj = get_object_or_404(District, pk=district_id)

    if request.method == 'GET':
        form = DistrictForm(instance=obj)
        return render_to_response('localites/ajouter_district.html', {'form': form, 'title': 'Editer un district'},
                                  context_instance=RequestContext(request))

    form = DistrictForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_district))
    else:
        return render_to_response('localites/ajouter_district.html', {'form': form, 'title': 'Editer un district'},
                                  context_instance=RequestContext(request))

def supprimer_district(request, district_id=None):
    obj = get_object_or_404(District, pk=district_id)
    obj.delete()
    json = simplejson.dumps([{'message': 'Enregistrement supprimé'}])
    return HttpResponse(json, mimetype='application/json')

def lister_commune(request):
    if request.method == 'GET':
        form = FiltreCommuneForm()
    else:
        form = FiltreCommuneForm(request.POST)
    header_link = '<a href="%s">&raquo; Ajouter une commune</a>' % (reverse(ajouter_commune),)
    page_js = '/media/js/localites/communes.js'
    title = 'Liste des communes'
    return render_to_response('layout_list.html', {"form": form, "title": title, "page_js": page_js, "header_link": header_link},
                              context_instance=RequestContext(request))

def ajouter_commune(request):
    if request.method == 'GET':
        form = CommuneForm()
        return render_to_response('localites/ajouter_commune.html', {'form': form, 'title': 'Ajouter une commune'},
                                  context_instance=RequestContext(request))

    form = CommuneForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_commune))
    else:
        return render_to_response('localites/ajouter_commune.html', {'form': form, 'title': 'Ajouter une commune'},
                                  context_instance=RequestContext(request))

def editer_commune(request, commune_id=None):
    obj = get_object_or_404(Commune, pk=commune_id)

    if request.method == 'GET':
        form = CommuneForm(instance=obj)
        return render_to_response('localites/ajouter_commune.html', {'form': form, 'title': 'Editer une commune'},
                                  context_instance=RequestContext(request))

    form = CommuneForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_commune))
    else:
        return render_to_response('localites/ajouter_commune.html', {'form': form, 'title': 'Editer une commune'},
                                  context_instance=RequestContext(request))

def supprimer_commune(request, commune_id=None):
    obj = get_object_or_404(Commune, pk=commune_id)
    obj.delete()
    json = simplejson.dumps([{'message': 'Enregistrement supprimé'}])
    return HttpResponse(json, mimetype='application/json')

def export_district(request):
    columns = [u'District', u'Code', u'Région']
    dataset = District.objects.filter_for_xls(request.GET)
    response = export_excel(columns, dataset, 'districts')
    return response

def ajax_district(request):
    # columns titles
    columns = ['nom', 'code', 'region', 'actions']

    # filtering
    post = process_datatables_posted_vars(request.POST)
    kwargs = {}
    if 'fDistrict' in post and post['fDistrict'] != '':
        kwargs['nom__icontains'] = str(post['fDistrict'])
    if 'fCode' in post and post['fCode'] != '':
        kwargs['code__icontains'] = post['fCode']
    if 'fRegion' in post and post['fRegion'] != '':
        kwargs['region'] = post['fRegion']

    records, total_records, display_records = query_datatables(District, columns, post, **kwargs)
    results = []
    for row in records:
        edit_link = '<a href="%s">[Edit]</a>' % (reverse(editer_district, args=[row.id]),)
        edit_link = '%s <a href="%s" class="del-link">[Suppr]</a>' % (edit_link, reverse(supprimer_district, args=[row.id]),)
        result = dict(
            nom = row.nom,
            code = row.code,
            region = row.region.nom,
            actions = edit_link,
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords":display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')


def export_commune(request):
    columns = [u'Commune', u'Code', u'Région', u'District', u'Guichet']
    dataset = Commune.objects.filter_for_xls(request.GET)
    response = export_excel(columns, dataset, 'communes')
    return response


def ajax_commune(request):
    # columns titles
    columns = ['nom', 'code', 'district__region', 'district', 'guichet', 'actions']

    # filtering
    post = process_datatables_posted_vars(request.POST)
    kwargs = {}
    if 'fCommune' in post and post['fCommune'] != '':
        kwargs['nom__icontains'] = str(post['fCommune'])
    if 'fCode' in post and post['fCode'] != '':
        kwargs['code__icontains'] = post['fCode']
    if 'fDistrict' in post and post['fDistrict'] != '':
        kwargs['district'] = post['fDistrict']
    else:
        if 'fRegion' in post and post['fRegion'] != '':
            kwargs['district__region'] = post['fRegion']

    records, total_records, display_records = query_datatables(Commune, columns, post, **kwargs)
    results = []
    for row in records:
        edit_link = '<a href="%s">[Edit]</a>' % (reverse(editer_commune, args=[row.id]),)
        edit_link = '%s <a href="%s" class="del-link">[Suppr]</a>' % (edit_link, reverse(supprimer_commune, args=[row.id]),)
        try:
            guichet = row.guichet
            guichet = '<a href="%s">%s</a>' % (reverse(editer_guichet, args=[guichet.id]), guichet.get_etat_display(),)
        except ObjectDoesNotExist:
            guichet = 'Non'

        result = dict(
            id = row.id,
            nom = row.nom,
            code = row.code,
            region = row.district.region.nom,
            district = row.district.nom,
            guichet = guichet,
            actions = edit_link,
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords": display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')

def select_district(request):
    region_id = int(request.POST['region'])

    districts = District.objects.filter(region=region_id).values('id', 'nom').order_by('nom')
    results = []
    for row in districts:
        results.append(dict(id=row['id'], nom=row['nom']))

    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')

def select_commune(request):
    commune_id = int(request.POST['district'])

    communes = Commune.objects.filter(district=commune_id).values('id', 'nom').order_by('nom')
    results = []
    for row in communes:
        results.append(dict(id=row['id'], nom=row['nom'].lower().capitalize()))

    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')


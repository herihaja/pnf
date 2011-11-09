# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from guichets.views import editer_guichet
from localites.models import Province, Region, District, Commune
from localites.forms import ProvinceForm, RegionForm, DistrictForm, CommuneForm, FiltreDistrictForm, FiltreCommuneForm
from helpers import paginate, process_datatables_posted_vars
import simplejson

def lister_province(request):
    page = int(request.GET.get('page', '1'))
    province_liste = []
    rows = Province.objects.all()

    if rows is not None:
        for row in rows:
            province_id = row.id
            lien_editer = reverse(editer_province, args=[province_id])
            lien_supprimer = reverse(supprimer_province, args=[province_id])
            province = dict(
                id=row.id,
                nom=row.nom,
                code=row.code,
                lien_editer=lien_editer,
                lien_supprimer=lien_supprimer
            )
            province_liste.append(province)

    provinces = paginate(province_liste, 25, page)

    return render_to_response('localites/lister_province.html', {"provinces": provinces},
                              context_instance=RequestContext(request))

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
    return render_to_response('localites/lister_region.html', context_instance=RequestContext(request))

def ajax_region(request):
    regions = Region.objects.all()
    iTotalRecords = Region.objects.all().count()
    iTotalDisplayRecords = iTotalRecords

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

    results = {"iTotalRecords": iTotalRecords, "iTotalDisplayRecords":iTotalDisplayRecords, "aaData": results}
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

def lister_district(request):
    if request.method == 'GET':
        form = FiltreDistrictForm()
    else:
        form = FiltreDistrictForm(request.POST)
    return render_to_response('localites/lister_district.html', {"form": form}, context_instance=RequestContext(request))

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
    # return HttpResponseRedirect(reverse(lister_district))
    json = simplejson.dumps([{'message': 'Enregistrement supprimé'}])
    return HttpResponse(json, mimetype='application/json')

def lister_commune(request):
    if request.method == 'GET':
        form = FiltreCommuneForm()
    else:
        form = FiltreCommuneForm(request.POST)
    return render_to_response('localites/lister_commune.html', {"form": form}, context_instance=RequestContext(request))

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
    # return HttpResponseRedirect(reverse(lister_commune))
    json = simplejson.dumps([{'message': 'Enregistrement supprimé'}])
    return HttpResponse(json, mimetype='application/json')

def ajax_district(request):
    # columns titles
    columns = ['nom', 'code', 'region', 'actions']

    # filtering
    posted = process_datatables_posted_vars(request.POST)
    
    kwargs = {}
    if 'fDistrict' in posted and posted['fDistrict'] != '':
        kwargs['nom__icontains'] = str(posted['fDistrict'])
    if 'fCode' in posted and posted['fCode'] != '':
        kwargs['code__icontains'] = posted['fCode']
    if 'fRegion' in posted and posted['fRegion'] != '':
        kwargs['region'] = posted['fRegion']
    
    # ordering
    sorts = []
    if 'iSortingCols' in posted:
        for i in range(0, int(posted['iSortingCols'])):
            sort_col = "iSortCol_%s" % (i,)
            sort_dir = posted["sSortDir_%s" % (i,)]
            if sort_dir == "asc":
                sort_qry = columns[int(posted[sort_col])]
            else:
                sort_qry = "-%s" % (columns[int(posted[sort_col])],)
            sorts.append(sort_qry)
    # limitting
    lim_start = None
    if 'iDisplayStart' in posted and posted['iDisplayLength'] != '-1':
        lim_start = int(posted['iDisplayStart'])
        lim_num = int(posted['iDisplayLength']) + lim_start

    # querying
    iTotalRecords = District.objects.count()
    if len(sorts) > 0:
        if lim_start is not None:
            district = District.objects.filter(**kwargs).order_by(*sorts)[lim_start:lim_num]
        else:
            district = District.objects.filter(**kwargs).order_by(*sorts)
    else:
        if lim_start is not None:
            district = District.objects.filter(**kwargs)[lim_start:lim_num]
        else:
            district = District.objects.filter(**kwargs)
    iTotalDisplayRecords = District.objects.filter(**kwargs).count()

    results = []

    for row in district:
        edit_link = '<a href="%s">[Edit]</a>' % (reverse(editer_district, args=[row.id]),)
        edit_link = '%s <a href="%s" class="del-link">[Suppr]</a>' % (edit_link, reverse(supprimer_district, args=[row.id]),)
        result = dict(
            nom = row.nom,
            code = row.code,
            region = row.region.nom,
            actions = edit_link,
        )
        results.append(result)

    sEcho = int(posted['sEcho'])
    results = {"iTotalRecords": iTotalRecords, "iTotalDisplayRecords":iTotalDisplayRecords, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')
    

def ajax_commune(request):
    # columns titles
    columns = ['nom', 'code', 'district__region', 'district', 'guichet', 'actions']

    # filtering
    posted = process_datatables_posted_vars(request.POST)

    kwargs = {}
    if 'fCommune' in posted and posted['fCommune'] != '':
        kwargs['nom__icontains'] = str(posted['fCommune'])
    if 'fCode' in posted and posted['fCode'] != '':
        kwargs['code__icontains'] = posted['fCode']
    if 'fDistrict' in posted and posted['fDistrict'] != '':
        kwargs['district'] = posted['fDistrict']
    else:
        if 'fRegion' in posted and posted['fRegion'] != '':
            kwargs['district__region'] = posted['fRegion']

    # ordering
    sorts = []
    if 'iSortingCols' in posted:
        for i in range(0, int(posted['iSortingCols'])):
            sort_col = "iSortCol_%s" % (i,)
            sort_dir = posted["sSortDir_%s" % (i,)]
            if sort_dir == "asc":
                sort_qry = columns[int(posted[sort_col])]
            else:
                sort_qry = "-%s" % (columns[int(posted[sort_col])],)
            sorts.append(sort_qry)
    # limitting
    lim_start = None
    if 'iDisplayStart' in posted and posted['iDisplayLength'] != '-1':
        lim_start = int(posted['iDisplayStart'])
        lim_num = int(posted['iDisplayLength']) + lim_start

    # querying
    iTotalRecords = Commune.objects.count()
    if len(sorts) > 0:
        if lim_start is not None:
            commune = Commune.objects.filter(**kwargs).order_by(*sorts)[lim_start:lim_num]
        else:
            commune = Commune.objects.filter(**kwargs).order_by(*sorts)
    else:
        if lim_start is not None:
            commune = Commune.objects.filter(**kwargs)[lim_start:lim_num]
        else:
            commune = Commune.objects.filter(**kwargs)
    iTotalDisplayRecords = Commune.objects.filter(**kwargs).count()

    results = []

    for row in commune:
        edit_link = '<a href="%s">[Edit]</a>' % (reverse(editer_commune, args=[row.id]),)
        edit_link = '%s <a href="%s" class="del-link">[Suppr]</a>' % (edit_link, reverse(supprimer_commune, args=[row.id]),)
        try:
            guichet = row.guichet
            guichet = '<a href="%s">%s</a>' % (reverse(editer_guichet, args=[guichet.id]), guichet.get_etat_display(),)
        except:
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

    sEcho = int(posted['sEcho'])
    results = {"iTotalRecords": iTotalRecords, "iTotalDisplayRecords":iTotalDisplayRecords, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')
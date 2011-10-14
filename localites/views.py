# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from localites.models import Province, Region, District, Commune
from localites.forms import ProvinceForm, RegionForm, DistrictForm, CommuneForm, FiltreDistrictForm, FiltreCommuneForm
from helpers import paginate, export_excel

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
    page = int(request.GET.get('page', '1'))
    region_liste = []
    rows = Region.objects.all()

    if rows is not None:
        for row in rows:
            region_id = row.id
            lien_editer = reverse(editer_region, args=[region_id])
            lien_supprimer = reverse(supprimer_region, args=[region_id])
            region = dict(
                id=row.id,
                nom=row.nom,
                code=row.code,
                province=row.province.nom,
                lien_editer=lien_editer,
                lien_supprimer=lien_supprimer
            )
            region_liste.append(region)

    regions = paginate(region_liste, 25, page)

    return render_to_response('localites/lister_region.html', {"regions": regions},
                              context_instance=RequestContext(request))

def ajouter_region(request):
    if request.method == 'GET':
        form = RegionForm()
        return render_to_response('localites/ajouter_region.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = RegionForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_region))
    else:
        return render_to_response('localites/ajouter_region.html', {'form': form},
                                  context_instance=RequestContext(request))

def editer_region(request, region_id=None):
    obj = get_object_or_404(Region, pk=region_id)

    if request.method == 'GET':
        form = RegionForm(instance=obj)
        return render_to_response('localites/ajouter_region.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = RegionForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_region))
    else:
        return render_to_response('localites/ajouter_region.html', {'form': form},
                                  context_instance=RequestContext(request))

def supprimer_region(request, region_id=None):
    obj = get_object_or_404(Region, pk=region_id)
    obj.delete()
    return HttpResponseRedirect(reverse(lister_region))

def lister_district(request):
    district_liste = []

    if request.method == 'GET':
        form = FiltreDistrictForm()
        rows = District.objects.all()
        page = int(request.GET.get('page', '1'))
    else:
        form = FiltreDistrictForm(request.POST)
        rows = District.objects.filtrer(request)
        page = int(request.POST['page'])

    if rows is not None:
        for row in rows:
            district_id = row.id
            lien_editer = reverse(editer_district, args=[district_id])
            lien_supprimer = reverse(supprimer_district, args=[district_id])
            district = dict(
                id=row.id,
                nom=row.nom,
                code=row.code,
                region=row.region.nom,
                lien_editer=lien_editer,
                lien_supprimer=lien_supprimer
            )
            district_liste.append(district)

    districts = paginate(district_liste, 25, page)

    return render_to_response('localites/lister_district.html', {"districts": districts, "form": form},
                              context_instance=RequestContext(request))

def ajouter_district(request):
    if request.method == 'GET':
        form = DistrictForm()
        return render_to_response('localites/ajouter_district.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = DistrictForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_district))
    else:
        return render_to_response('localites/ajouter_district.html', {'form': form},
                                  context_instance=RequestContext(request))

def editer_district(request, district_id=None):
    obj = get_object_or_404(District, pk=district_id)

    if request.method == 'GET':
        form = DistrictForm(instance=obj)
        return render_to_response('localites/ajouter_district.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = DistrictForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_district))
    else:
        return render_to_response('localites/ajouter_district.html', {'form': form},
                                  context_instance=RequestContext(request))

def supprimer_district(request, district_id=None):
    obj = get_object_or_404(District, pk=district_id)
    obj.delete()
    return HttpResponseRedirect(reverse(lister_district))

def lister_commune(request):
    commune_liste = []

    if request.method == 'GET':
        form = FiltreCommuneForm()
        rows = Commune.objects.all()
        page = int(request.GET.get('page', '1'))
    else:
        form = FiltreCommuneForm(request.POST)
        rows = Commune.objects.filtrer(request)
        page = int(request.POST['page'])

    if rows is not None:
        for row in rows:
            commune_id = row.id
            lien_editer = reverse(editer_commune, args=[commune_id])
            lien_supprimer = reverse(supprimer_commune, args=[commune_id])
            commune = dict(
                id=row.id,
                nom=row.nom,
                code=row.code,
                district=row.district.nom,
                region=row.district.region.nom,
                lien_editer=lien_editer,
                lien_supprimer=lien_supprimer
            )
            commune_liste.append(commune)

    communes = paginate(commune_liste, 25, page)

    return render_to_response('localites/lister_commune.html', {"communes": communes, "form": form},
                              context_instance=RequestContext(request))

def ajouter_commune(request):
    if request.method == 'GET':
        form = CommuneForm()
        return render_to_response('localites/ajouter_commune.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = CommuneForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_commune))
    else:
        return render_to_response('localites/ajouter_commune.html', {'form': form},
                                  context_instance=RequestContext(request))

def editer_commune(request, commune_id=None):
    obj = get_object_or_404(Commune, pk=commune_id)

    if request.method == 'GET':
        form = CommuneForm(instance=obj)
        return render_to_response('localites/ajouter_commune.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = CommuneForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_commune))
    else:
        return render_to_response('localites/ajouter_commune.html', {'form': form},
                                  context_instance=RequestContext(request))

def supprimer_commune(request, commune_id=None):
    obj = get_object_or_404(Commune, pk=commune_id)
    obj.delete()
    return HttpResponseRedirect(reverse(lister_commune))
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from models import Province, Region, District, Commune
from forms import ProvinceForm, RegionForm, DistrictForm, CommuneForm

def lister_province(request):
    return render_to_response('localites/lister_province.html', {"nodes": lignes},
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

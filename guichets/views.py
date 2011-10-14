# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from guichets.models import Guichet
from guichets.forms import GuichetForm, FiltreGuichetForm
from helpers import paginate, export_excel

def lister_guichet(request):
    guichet_liste = []

    if request.method == 'GET':
        form = FiltreGuichetForm()
        rows = Guichet.objects.all()
        page = int(request.GET.get('page', '1'))
    else:
        form = FiltreGuichetForm(request.POST)
        rows = Guichet.objects.filtrer(request)
        page = int(request.POST['page'])

    if rows is not None:
        for row in rows:
            guichet_id = row.id
            lien_editer = reverse(editer_guichet, args=[guichet_id])
            lien_supprimer = reverse(supprimer_guichet, args=[guichet_id])
            guichet = dict(
                id=row.id,
                nom=row.nom,
                lien_editer=lien_editer,
                lien_supprimer=lien_supprimer
            )
            guichet_liste.append(guichet)

    guichets = paginate(guichet_liste, 25, page)

    return render_to_response('guichets/lister_guichet.html', {"guichets": guichets, "form": form},
                              context_instance=RequestContext(request))

def ajouter_guichet(request):
    if request.method == 'GET':
        form = GuichetForm()
        return render_to_response('guichets/ajouter_guichet.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = GuichetForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_guichet))
    else:
        return render_to_response('guichets/ajouter_guichet.html', {'form': form},
                                  context_instance=RequestContext(request))

def editer_guichet(request, guichet_id=None):
    obj = get_object_or_404(Guichet, pk=guichet_id)

    if request.method == 'GET':
        form = GuichetForm(instance=obj)
        return render_to_response('guichets/ajouter_guichet.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = GuichetForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_guichet))
    else:
        return render_to_response('guichets/ajouter_guichet.html', {'form': form},
                                  context_instance=RequestContext(request))

def supprimer_guichet(request, guichet_id=None):
    obj = get_object_or_404(Guichet, pk=guichet_id)
    obj.delete()
    return HttpResponseRedirect(reverse(lister_guichet))
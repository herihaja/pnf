# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from bailleurs.models import Bailleur
from bailleurs.forms import BailleurForm, FiltreBailleurForm
from helpers import paginate, export_excel

def lister_bailleur(request):
    bailleur_liste = []

    if request.method == 'GET':
        form = FiltreBailleurForm()
        rows = Bailleur.objects.all()
        page = int(request.GET.get('page', '1'))
    else:
        form = FiltreBailleurForm(request.POST)
        rows = Bailleur.objects.filtrer(request)
        page = int(request.POST['page'])

    if rows is not None:
        for row in rows:
            bailleur_id = row.id
            lien_editer = reverse(editer_bailleur, args=[bailleur_id])
            lien_supprimer = reverse(supprimer_bailleur, args=[bailleur_id])
            bailleur = dict(
                id=row.id,
                nom=row.nom,
                lien_editer=lien_editer,
                lien_supprimer=lien_supprimer
            )
            bailleur_liste.append(bailleur)

    bailleurs = paginate(bailleur_liste, 25, page)

    return render_to_response('bailleurs/lister_bailleur.html', {"bailleurs": bailleurs, "form": form},
                              context_instance=RequestContext(request))

def ajouter_bailleur(request):
    if request.method == 'GET':
        form = BailleurForm()
        return render_to_response('bailleurs/ajouter_bailleur.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = BailleurForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_bailleur))
    else:
        return render_to_response('bailleurs/ajouter_bailleur.html', {'form': form},
                                  context_instance=RequestContext(request))

def editer_bailleur(request, bailleur_id=None):
    obj = get_object_or_404(Bailleur, pk=bailleur_id)

    if request.method == 'GET':
        form = BailleurForm(instance=obj)
        return render_to_response('bailleurs/ajouter_bailleur.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = BailleurForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(lister_bailleur))
    else:
        return render_to_response('bailleurs/ajouter_bailleur.html', {'form': form},
                                  context_instance=RequestContext(request))

def supprimer_bailleur(request, bailleur_id=None):
    obj = get_object_or_404(Bailleur, pk=bailleur_id)
    obj.delete()
    return HttpResponseRedirect(reverse(lister_bailleur))
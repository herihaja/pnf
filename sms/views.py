# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from sms.models import Reception, Envoi
from sms.forms import FiltreEnvoiForm, FiltreReceptionForm
from helpers import paginate, export_excel

def lister_reception(request):
    reception_liste = []

    if request.method == 'GET':
        form = FiltreReceptionForm()
        rows = Reception.objects.all()
        page = int(request.GET.get('page', '1'))
    else:
        form = FiltreReceptionForm(request.POST)
        rows = Reception.objects.filtrer(request)
        page = int(request.POST['page'])

    if rows is not None:
        for row in rows:
            reception_id = row.id
            lien_editer = reverse(editer_reception, args=[reception_id])
            lien_supprimer = reverse(supprimer_reception, args=[reception_id])
            reception = dict(
                id=row.id,
                date_reception = row.date_reception,
                expediteur = row.expediteur,
                message = row.message,
                statut = row.statut,
                lien_editer=lien_editer,
                lien_supprimer=lien_supprimer
            )
            reception_liste.append(reception)

    receptions = paginate(reception_liste, 25, page)

    return render_to_response('sms/lister_reception.html', {"receptions": receptions, "form": form},
                              context_instance=RequestContext(request))

def lister_envoi(request):
    envoi_liste = []

    if request.method == 'GET':
        form = FiltreEnvoiForm()
        rows = Envoi.objects.all()
        page = int(request.GET.get('page', '1'))
    else:
        form = FiltreEnvoiForm(request.POST)
        rows = Envoi.objects.filtrer(request)
        page = int(request.POST['page'])

    if rows is not None:
        for row in rows:
            envoi_id = row.id
            lien_editer = reverse(editer_envoi, args=[envoi_id])
            lien_supprimer = reverse(supprimer_envoi, args=[envoi_id])
            envoi = dict(
                id=row.id,
                date_envoi = row.date_envoi,
                destinataire = row.destinataire,
                message = reow.message,
                lien_editer=lien_editer,
                lien_supprimer=lien_supprimer
            )
            envoi_liste.append(envoi)

    envois = paginate(envoi_liste, 25, page)

    return render_to_response('sms/lister_envoi.html', {"envois": envois, "form": form},
                              context_instance=RequestContext(request))

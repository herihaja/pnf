# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from compteur.forms import CompteurForm, CompteurRechargeForm
from compteur.models import Compteur, Log


@login_required(login_url="/connexion")
def index(request):
    compteurs = Compteur.objects.all()
    data = []
    for compteur in compteurs:
        link_ajout = reverse(ajoute_credit, args=[compteur.id])
        link_ajuste = reverse(edit_compteur, args=[compteur.id])
        data.append({
            'operateur': compteur.get_operateur_display(),
            'prix': compteur.prix,
            'solde': compteur.credit,
            'link_ajout': link_ajout,
            'link_ajuste': link_ajuste,
        })

    return render_to_response('compteur/index.html', {"data": data},
                                  context_instance=RequestContext(request))

@login_required(login_url="/connexion")
def ajoute_credit(request, compteur_id=None):
    obj = get_object_or_404(Compteur, pk=compteur_id)
    title = u"Ajouteur du crédit %s" % (obj.get_operateur_display(),)

    if request.method == 'GET':
        form = CompteurRechargeForm(instance=obj)
        return render_to_response('compteur/edit.html', {'form': form, 'title': title},
                                  context_instance=RequestContext(request))

    form = CompteurRechargeForm(request.POST, instance=obj)
    if form.is_valid():
        obj.credit = obj.credit + int(form.cleaned_data['recharge'])
        obj.save()

        # logger action
        compteur_log = Log(
            operateur = obj.operateur,
            operation = 1,
            credit = int(form.cleaned_data['recharge'])
        )
        compteur_log.save()

        return HttpResponseRedirect(reverse(index))
    else:
        return render_to_response('compteur/edit.html', {'form': form, 'title': title},
                                  context_instance=RequestContext(request))


@login_required(login_url="/connexion")
def edit_compteur(request,  compteur_id=None):
    obj = get_object_or_404(Compteur, pk=compteur_id)

    if request.method == 'GET':
        form = CompteurForm(instance=obj)
        return render_to_response('compteur/edit.html', {'form': form, 'title': 'Ajouteur du crédit'},
                                  context_instance=RequestContext(request))

    form = CompteurForm(request.POST, instance=obj)
    if form.is_valid():
        # logger action
        if obj.credit != int(form.cleaned_data['credit']):
            compteur_log = Log(
                operateur = obj.operateur,
                operation = 2,
                credit = int(form.cleaned_data['credit'])
            )
            compteur_log.save()

        # enregistrer
        form.save()
        return HttpResponseRedirect(reverse(index))
    else:
        return render_to_response('compteur/edit.html', {'form': form, 'title': 'Ajouteur du crédit'},
                                  context_instance=RequestContext(request))


def update_credit_after_send(operateur):
    obj = get_object_or_404(Compteur, pk=operateur)
    if obj.credit > 0:
        solde = obj.credit - obj.prix
        if solde > 0:
            obj.credit = solde
            obj.save()

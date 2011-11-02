# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
import datetime
from donnees.models import Donnees
from guichets.models import Guichet
from sms.models import Reception, Envoi
from sms.forms import FiltreEnvoiForm, FiltreReceptionForm, TesterForm
from helpers import paginate, export_excel
import re
from django.db.models import Q

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
        if request.POST['action'] == 'export':
            return export(rows)

    if rows is not None:
        for row in rows:
            reception_id = row.id
            lien_editer = 'to_replace'#reverse(editer_reception, args=[reception_id])
            lien_supprimer = 'to_replace'#reverse(supprimer_reception, args=[reception_id])
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


def sms_tester(request):
    if request.method == 'GET':
        form = TesterForm()
        return render_to_response('sms/tester.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = TesterForm(request.POST)
    if form.is_valid():
        data, message_retour = _parser(request.POST['message'])

        if len(data) == 12:
            reception = Reception(
                date_reception = datetime.datetime.now(),
                expediteur = request.POST['expediteur'],
                message = request.POST['message'],
                statut = 1,
                retour = message_retour
            )
            reception.save()

            donnees = Donnees(
                commune = data['commune'],
                sms = reception.insert_id(),
                periode = data['periode'],
                demandes = data['demandes'],
                oppositions = data['oppositions'],
                resolues = data['resolues'],
                certificats = data['certificats'],
                femmes = data['femmes'],
                surfaces = data['surfaces'],
                recettes = data['recettes'],
                garanties = data['garanties'],
                reconnaissances = data['reconnaissances'],
                mutations = data['mutations'],
            )
            donnees.save()
        else:
            Reception(
                date_reception = datetime.datetime.now(),
                expediteur = request.POST['expediteur'],
                message = request.POST['message'],
                statut = 2,
                retour = message_retour
            )
        return HttpResponseRedirect(reverse(lister_reception))
    else:
        return render_to_response('sms/tester.html', {'form': form},
                                  context_instance=RequestContext(request))


def export(rows):
    header = ['Date de reception', 'Expediteur','Message', 'Statut', 'retour']
    liste = []
    for row in rows:
        cleaned_row = [row.date_reception, row.expediteur, row.message, row.statut, row.retour]
        liste.append(cleaned_row)
    ret = export_excel(header, liste, 'reçus')
    return ret

def _parser(message):
    data = []
    tokens = re.split(' \.', message)

    if len(tokens) < 12:
        return data, u"Nombre de données insuffisant"

    if len(tokens) > 12:
        return data, u"Nombre de données en dépassement"

    expediteur = tokens.pop(0)
    expediteur = expediteur.split('#')
    if len(expediteur) < 2:
        return data, u"Code AGF ou mot de passe non fourni"
    elif len(expediteur) > 2:
        return data, u"Code AGF erroné"
    else:
        # vérifier mot de passe
        #ADEFFD#675333 .p 11.2010 .d 1000 .o 1200 .r 2000 .c 3000 .f 0000 .t 1000 .a 1000000000 .s 0,233 .g 1000 .m 2000
        agf = Guichet.objects.filter((Q(agf1=expediteur[0]) & Q(password1=expediteur[1])) | (Q(agf2=expediteur[0]) & Q(password2=expediteur[1])))

        mapping = {'p': 'periode', 'd': 'demandes', 'o': 'oppositions', 'r': 'resolues', 'c': 'certificats', 'f': 'femmes',
                   't': 'reconnaissances', 'a': 'recettes', 's': 'surfaces', 'g': 'garanties', 'm': 'mutations'}

        if len(agf) == 1:
            data['commune'] = agf.commune
            for token in tokens:
                token = token.strip()
                token = token.split
                if token[0] in mapping:
                    if token[0] == 'p':
                        periode = token[1].split('.')
                        if len(periode[0]) > 2 or len(periode[1]) < 4:
                            return data, u"Date erronée"
                        else:
                            data['periode'] = '%s-%s-01' & (periode[1], periode[0])
                    else:
                        data[mapping[token[0]]] = int(token[1])
                else:
                    return data, u"Code question '%s' inconnu" % token[0]
            return data, u"Félicitations! Données enregistrées"
        else:
            return data, u"Code AGF ou mot de passe erroné"
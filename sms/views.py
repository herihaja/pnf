# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from donnees.models import Donnees, Recu
from guichets.models import Guichet
from sms.models import Reception, Envoi, Communication
from sms.forms import FiltreEnvoiForm, FiltreReceptionForm, TesterForm
from helpers import export_excel, process_datatables_posted_vars, query_datatables
import re
from django.db.models import Q
import simplejson

def lister_reception(request, statut=1):
    if request.method == 'GET':
        form = FiltreReceptionForm(initial={'statut': statut})
    else:
        form = FiltreReceptionForm(request.POST, initial={'statut': statut})
    page_js = '/media/js/sms/reception.js'
    if statut == 1:
        title = 'Sms corrects'
    elif statut == 2:
        title = 'Sms inconnus'
    else:
        title = 'Sms erronés'
    return render_to_response('layout_list.html', {"form": form, "title": title, "page_js": page_js},
                              context_instance=RequestContext(request))

def ajax_reception(request):
    # columns titles
    columns = ['date_reception', 'numero', 'message', 'statut', 'reponse']

    # filtering
    post = process_datatables_posted_vars(request.POST)

    kwargs = {}
    if 'fExpediteur' in post and post['fExpediteur'] != '':
        kwargs['expediteur__icontains'] = str(post['fExpediteur'])
    if 'fMessage' in post and post['fMessage'] != '':
        kwargs['message__icontains'] = post['fMessage']
    if 'fStatut' in post and post['fStatut'] != '':
        kwargs['statut'] = post['fStatut']
    if 'fCreede' in post and post['fCreede'] != '':
        cree_de = datetime.strptime(post['fCreede'], "%d/%m/%Y")
        cree_de = datetime.strftime(cree_de, "%Y-%m-%d")
        kwargs['date_reception__gte'] = cree_de
    if 'fCreea' in post and post['fCreea'] != '':
        cree_a = datetime.strptime(post['fCreea'], "%d/%m/%Y")
        cree_a = datetime.strftime(cree_a, "%Y-%m-%d")
        kwargs['date_reception__lte'] = cree_a

    records, total_records, display_records = query_datatables(Reception, columns, post, **kwargs)
    results = []
    for row in records:
        result = dict(
            date_reception = datetime.strftime(row.date_reception, "%d-%m-%Y %H:%M:%S"),
            numero = row.expediteur,
            message = row.message,
            reponse = row.retour,
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords":display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')

def export_reception(request):
    columns = [u'Date / Heure', u'Expéditeur', u'Message', u'Statut', u'Réponse']
    dataset = Reception.objects.filter_for_xls(request.GET)
    response = export_excel(columns, dataset, 'sms')
    return response

def lister_envoi(request):
    if request.method == 'GET':
        form = FiltreEnvoiForm()
    else:
        form = FiltreEnvoiForm(request.POST)
    page_js = '/media/js/sms/envois.js'
    title = 'Sms envoyés'
    return render_to_response('layout_list.html', {"form": form, "title": title, "page_js": page_js},
                              context_instance=RequestContext(request))

def ajax_envoi(request):
    # columns titles
    columns = ['date_envoi', 'numero', 'message', 'statut', 'reponse']

    # filtering
    post = process_datatables_posted_vars(request.POST)

    kwargs = {}
    if 'fDestinataire' in post and post['fDestinataire'] != '':
        kwargs['destinataire__icontains'] = str(post['fDestinataire'])
    if 'fMessage' in post and post['fMessage'] != '':
        kwargs['message__icontains'] = post['fMessage']
    if 'fCreede' in post and post['fCreede'] != '':
        cree_de = datetime.strptime(post['fCreede'], "%d/%m/%Y")
        cree_de = datetime.strftime(cree_de, "%Y-%m-%d")
        kwargs['date_envoi__gte'] = cree_de
    if 'fCreea' in post and post['fCreea'] != '':
        cree_a = datetime.strptime(post['fCreea'], "%d/%m/%Y")
        cree_a = datetime.strftime(cree_a, "%Y-%m-%d")
        kwargs['date_envoi__lte'] = cree_a

    records, total_records, display_records = query_datatables(Envoi, columns, post, **kwargs)
    results = []

    for row in records:
        result = dict(
            date_envoi = datetime.strftime(row.date_envoi, "%d-%m-%Y %H:%M:%S"),
            numero = row.destinataire,
            message = row.message,
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords":display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')

def export_envoi(request):
    columns = [u'Date / Heure', u'Destinataire', u'Message']
    dataset = Envoi.objects.filter_for_xls(request.GET)
    response = export_excel(columns, dataset, 'sms')
    return response

def sms_tester(request):
    if request.method == 'GET':
        form = TesterForm()
        return render_to_response('sms/tester.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = TesterForm(request.POST)
    if form.is_valid():
        date_reception = datetime.now()
        type_sms, reponse, data, texte = _parser(request.POST['message'])

        if type_sms == 1:
            reception = Reception(
                date_reception = date_reception,
                expediteur = request.POST['expediteur'],
                message = request.POST['message'],
                statut = 1,
                retour = reponse,
            )
            reception.save()

            donnees = Recu(
                commune = data['commune'],
                sms = reception,
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

            if texte != '':
                message = Communication(
                    commune = data['commune'],
                    sms = reception,
                    date_reception = date_reception,
                    message = texte,
                )
                message.save()
        else:
            reception = Reception(
                date_reception = date_reception,
                expediteur = request.POST['expediteur'],
                message = request.POST['message'],
                statut = type_sms,
                retour = reponse,
            )
            reception.save()
        return HttpResponseRedirect(reverse(lister_reception, args=[type_sms]))
    else:
        return render_to_response('sms/tester.html', {'form': form},
                                  context_instance=RequestContext(request))

def _parser(message):
    data = {}
    reponse = ''
    texte = ''
    type_sms = 1

    sms_parts = message.split('#')
    
    expediteur = sms_parts[0]
    indicateurs = sms_parts[1]
    if len(sms_parts) > 2:
        texte = sms_parts[2]

    # vérifier le code agf en premier
    agf = Guichet.objects.filter(Q(agf1=expediteur) | Q(agf2=expediteur))
    if len(agf) == 0:
        reponse = u"Erreur, AGF inconnu"
        type_sms = 3
    else:
        agf = agf[0]
        # envoyeur 1 ou 2
        if agf.agf1 == expediteur:
            password1 = 'password1'
        else:
            password1 = 'password2'

        tokens = re.split(' \.', indicateurs)
        password = tokens.pop(0)

        # verifier mot de passe
        kwargs = {password1: password}
        agf = Guichet.objects.filter(**kwargs)
        if len(agf) == 0:
            reponse = u"Mot de passe erroné"
            type_sms = 2
        else:
            agf = agf[0]
            if len(tokens) < 11:
                message = u"Erreur, Nombre de données insuffisant"
                type_sms = 2
            elif len(tokens) > 11:
                return data, u"Erreur, Nombre de données en dépassement"
                type_sms = 2
            else:
                mapping = {'p': 'periode', 'd': 'demandes', 'o': 'oppositions', 'r': 'resolues', 'c': 'certificats', 'f': 'femmes',
                           't': 'reconnaissances', 'a': 'recettes', 's': 'surfaces', 'g': 'garanties', 'm': 'mutations'}

                data['commune'] = agf.commune
                for token in tokens:
                    token = token.strip()
                    token = token.split()
                    if len(token) == 2:
                        if token[0] in mapping:
                            if token[0] == 'p':
                                periode = token[1].split('.')
                                if len(periode[0]) > 2 or len(periode[1]) < 4:
                                    reponse = u"Date erronée"
                                    type_sms = 2
                                else:
                                    data['periode'] = '%s-%s-01' % (periode[1], periode[0])
                            elif token[0] == 's' or token[0] == 'a':
                                value = token[1]
                                value.replace(',', '.')
                                data[mapping[token[0]]] = float(value)
                            else:
                                data[mapping[token[0]]] = token[1]
                        else:
                            reponse = u"Erreur, Code question '%s' inconnu" % token[0]
                            type_sms = 2
                    else:
                        reponse = u"Erreur, Réponse '%s' erronée ou manquante" % token[0]
                        type_sms = 2

                # controle de coherence
                if type_sms == 1:
                    if data['femmes'] > data['certificats']:
                        reponse = u"Erreur, certificats donnés à des femmes ne peut dépasser le nombre de certificats délivrés"
                        type_sms = 2
                    else:
                        reponse = u"Félicitations! Données enregistrées"
                        type_sms = 1

    return type_sms, reponse, data, texte

def lister_communication(request):
    if request.method == 'GET':
        form = FiltreReceptionForm()
    else:
        form = FiltreReceptionForm(request.POST)
    page_js = '/media/js/sms/messages.js'
    title = 'Messages'
    return render_to_response('layout_list_no_form.html', {"form": form, "title": title, "page_js": page_js},
                              context_instance=RequestContext(request))

def ajax_communication(request):
    # columns titles
    columns = ['date_reception', 'commune', 'code', 'message']

    # filtering
    post = process_datatables_posted_vars(request.POST)
    kwargs = {}
    records, total_records, display_records = query_datatables(Communication, columns, post, **kwargs)
    results = []
    for row in records:
        result = dict(
            date_reception = datetime.strftime(row.date_reception, "%d-%m-%Y %H:%M:%S"),
            commune = row.commune.nom,
            code = row.commune.code,
            message = row.message,
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords":display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')
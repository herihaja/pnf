# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from donnees.models import Recu
from gammu.models import Outbox
from guichets.models import Guichet, Rma
from sms.models import Reception, Envoi, Communication
from sms.forms import FiltreEnvoiForm, FiltreReceptionForm, TesterForm, BroadcastForm, FiltreCommunicationForm
from helpers import export_excel, process_datatables_posted_vars, query_datatables, export_pdf
import re
from django.db.models import Q
import simplejson

RECIPIENT_LIST = ['orange', 'airtel', 'telma']
mapping = {'p': 'periode', 'd': 'demandes', 'o': 'oppositions', 'r': 'resolues', 'k': 'certificats', 'f': 'femmes',
                           't': 'reconnaissances', 'a': 'recettes', 's': 'surfaces', 'g': 'garanties', 'm': 'mutations'}
erreur_indic = {
    'd': u"Ny isan'ny Fangatahana (Demandes) dia tokony ho 0 na mihoatra",
    'o': u"Ny isan'ny Fanoherana voaray (Oppositions) dia tokony ho tokony ho 0 na mihoatra",
    'r': u"Ny isan'ny Fanoherana nahitana vahaolana (Oppositions résolues) dia tokony ho 0 na mihoatra",
    'k': u"Ny isan'ny Karatany voasoratra (certificats délivrés) dia tokony ho 0 na mihoatra",
    'f': u"Ny isan'ny Karatany amin’ny anaran'ny vehivavy (certificats accordés à des femmes) dia tokony ho 0 na mihoatra",
    't': u"Ny isan'ny Fangatahana nahavitàna fitsirihina (Reconnaissances locales effectuées) dia tokony ho 0 na mihoatra",
    'a': u"Ny Vola niditra (recettes) dia tokony ho 0 na mihoatra",
    's': u"Ny Fitambaran'ny velaran-tany t@ ireo karatany voasora (Superficie totale) dia tokony ho 0 na mihoatra",
    'g': u"Ny isan'ny Certificats nampiasaina natao antoka (certificats utilisés comme garanties à des banques) dia tokony ho 0 na mihoatra",
    'm': u"Ny isan'ny Famindràna tany (mutations) dia tokony ho 0 na mihoatra",
}


@login_required(login_url="/connexion")
def lister_reception(request, statut='1'):
    if request.method == 'GET':
        form = FiltreReceptionForm(initial={'statut': statut})
    else:
        form = FiltreReceptionForm(request.POST, initial={'statut': statut})
    page_js = '/media/js/sms/reception.js'
    if statut == '1':
        title = 'Sms corrects'
    elif statut == '2':
        title = 'Sms erronés'
    else:
        title = 'Sms inconnus'
    return render_to_response('layout_list.html', {"form": form, "title": title, "page_js": page_js},
                              context_instance=RequestContext(request))


@login_required(login_url="/connexion")
def supprimer_sms(request, sms_id=None):
    if request.method == "POST":
        selected = request.POST.getlist("selected[]")
        obj = Reception.objects.filter(pk__in = selected)
    else:
        obj = get_object_or_404(Reception, pk=sms_id)
    obj.delete()
    json = simplejson.dumps([{'message': 'Enregistrement supprimé'}])
    return HttpResponse(json, mimetype='application/json')


@login_required(login_url="/connexion")
def supprimer_envoi(request, sms_id=None):
    if request.method == "POST":
        selected = request.POST.getlist("selected[]")
        obj = Envoi.objects.filter(pk__in = selected)
    else:
        obj = get_object_or_404(Envoi, pk=sms_id)
    obj.delete()
    json = simplejson.dumps([{'message': 'Enregistrement supprimé'}])
    return HttpResponse(json, mimetype='application/json')


def ajax_reception(request):
    # columns titles
    columns = ['date_reception', 'expediteur', 'message', 'statut', 'reponse']

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
        edit_link = '<a href="%s" class="del-link">[Suppr]</a>' % ( reverse(supprimer_sms, args=[row.id]),)
        checkbox  = '<input type="checkbox" name=\"selected\" class="check-element" value="%s"/>' % row.id
        result = dict(
            date_reception = datetime.strftime(row.date_reception, "%d-%m-%Y %H:%M:%S"),
            numero = row.expediteur,
            message = row.message,
            reponse = row.retour,
            actions = edit_link,
            checkbox = checkbox,
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords":display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')


@login_required(login_url="/connexion")
def export_reception(request, filetype=None):
    columns = [u'Date / Heure', u'Expéditeur', u'Message', u'Statut', u'Réponse']
    dataset = Reception.objects.filter_for_xls(request.GET)
    if filetype == 'xls':
        response = export_excel(columns, dataset, 'sms')
    else:
        response = export_pdf(columns, dataset, 'sms', 1)
    return response


@login_required(login_url="/connexion")
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
        edit_link = '<a href="%s" class="del-link">[Suppr]</a>' % ( reverse(supprimer_envoi, args=[row.id]),)
        checkbox  = '<input type="checkbox" name=\"selected\" class="check-element" value="%s"/>' % row.id
        result = dict(
            date_envoi = datetime.strftime(row.date_envoi, "%d-%m-%Y %H:%M:%S"),
            numero = row.destinataire,
            message = row.message,
            actions = edit_link,
            checkbox = checkbox,
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords":display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')


@login_required(login_url="/connexion")
def export_envoi(request, filetype=None):
    columns = [u'Date / Heure', u'Destinataire', u'Message']
    dataset = Envoi.objects.filter_for_xls(request.GET)
    if filetype == 'xls':
        response = export_excel(columns, dataset, 'sms')
    else:
        response = export_pdf(columns, dataset, 'sms', 1)
    return response


@login_required(login_url="/connexion")
def sms_tester(request):
    if request.method == 'GET':
        form = TesterForm()
        return render_to_response('sms/tester.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = TesterForm(request.POST)
    if form.is_valid():
        receiving_date = datetime.now()
        type_sms = process_sms(request.POST['expediteur'], request.POST['message'], receiving_date, 'tester')

        # afficher le sms reçu
        return HttpResponseRedirect(reverse(lister_reception, args=[type_sms]))
    else:
        return render_to_response('sms/tester.html', {'form': form},
                                  context_instance=RequestContext(request))


def process_sms(sendernumber, message, receiving_date, recipient=None):
    type_sms, reponse, data, texte = _parser_sms(message)

    # enregistrer le sms
    reception = Reception(
            date_reception = receiving_date,
            expediteur = sendernumber,
            message = message,
            statut = type_sms,
            retour = reponse,
        )
    reception.save()

    if type_sms != 3 and 'periode' in data:
        rma = Rma(
            guichet = data['guichet'],
            sms = reception,
            periode = data['periode'],
            agf = data['agf'],
        )
        rma.save()

    # si message valide enregistrer pour test
    if type_sms == 1:
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
            texte = 'tsy misy'
        message = Communication(
            commune = data['commune'],
            sms = reception,
            date_reception = receiving_date,
            message = texte,
        )
        message.save()


    # message de retour
    if recipient != 'tester' and type_sms != 3:
        if recipient in RECIPIENT_LIST:
            send_sms(recipient, sendernumber, reponse)

    return type_sms


def cron_process_sms(sms):
    # marquer comme traite
    sms.processed = True
    sms.save()

    #traiter
    if sms.sendernumber != '0335600080':
        process_sms(sms.sendernumber, sms.textdecoded, sms.receivingdatetime, sms.recipientid)




def _parser_sms(message):
    data = {}
    reponse = ''
    texte = ''
    type_sms = 1

    sms_parts = message.split('#')

    # vérifier le code agf en premier
    agf = Guichet.objects.filter(Q(agf1=sms_parts[0]) | Q(agf2=sms_parts[0]))
    if len(agf) == 0:
        reponse = u"Diso ny Kaody AGF nalefanao"
        type_sms = 3
    else:
        agf = agf[0]
        data['guichet'] = Guichet.objects.get(pk=agf.id)

        expediteur = sms_parts[0]
        data['agf'] = expediteur

        if len(sms_parts) == 1:
            reponse = u"Tsy ampy 14 ny isan'ny valinteny nalefanao. Amarino tsirairay ny kaodin'ny fanontaniana sy ny valiny mifanaraka aminy"
            type_sms = 2
        else:
            indicateurs = sms_parts[1]
            if len(sms_parts) > 2:
                texte = sms_parts[2]

            tokens = re.split(' \.', indicateurs)
            password = tokens.pop(0)

            # verifier mot de passe
            # envoyeur 1 ou 2
            if agf.agf1 == expediteur and agf.password1 != password:
                reponse = u"Diso ny kaody miafina"
                type_sms = 2
            elif agf.agf2 == expediteur and agf.password2 != password:
                reponse = u"Diso ny kaody miafina"
                type_sms = 2
            else:
                if len(tokens) < 11:
                    reponse = u"Tsy ampy 14 ny isan'ny valinteny nalefanao. Amarino tsirairay ny kaodin'ny fanontaniana sy ny valiny mifanaraka aminy"
                    type_sms = 2
                elif len(tokens) > 11:
                    reponse = u"Diso! Mihoatra ny 14 ny isan'ny valinteny nalefanao.  Amarino tsirairay ny kaodin'ny fanontaniana sy ny valiny mifanaraka aminy"
                    type_sms = 2
                
                data['commune'] = agf.commune
                for token in tokens:
                    token = token.strip()
                    token = token.split()
                    if token[0] in mapping:
                        if len(token) == 2:
                            periode_correct = True
                            if token[0] == 'p':
                                periode = token[1].split('.')
                                if len(periode) == 2:
                                    if len(periode[1]) == 2:
                                        annee = "20%s" % (periode[1],)
                                    elif len(periode[1]) == 4:
                                        annee = periode[1]
                                    else:
                                        reponse = u"Diso ny daty nalefanao fa tokony ho mm.aaaa ny paoziny"
                                        type_sms = 2
                                        periode_correct = False
                                else:
                                    reponse = u"Diso ny daty nalefanao fa tokony ho mm.aaaa ny paoziny"
                                    type_sms = 2
                                    periode_correct = False


                                if len(periode[0]) == 1:
                                    mois = "0%s" % (periode[0],)
                                elif len(periode[0]) == 2:
                                    mois = periode[0]
                                else:
                                    reponse = u"Diso ny daty nalefanao fa tokony ho mm.aaaa ny paoziny"
                                    type_sms = 2
                                    periode_correct = False

                                if periode_correct:
                                    periode = '%s-%s-01' % (annee, mois)
                                    date_envoye = datetime.strptime(periode, '%Y-%m-%d').date()
                                    date_now = datetime.now()
                                    date_now = "%s-%s-01" % (date_now.year, date_now.month,)
                                    date_now = datetime.strptime(date_now, '%Y-%m-%d').date()
                                    diff = date_envoye - date_now
                                    if diff >= timedelta(days = 0):
                                        reponse = u"Tokony ho volana alohan'izao volana iainantsika izao no eo amin'ny daty"
                                        type_sms = 2
                                    else:
                                        data['periode'] = periode
                            elif token[0] == 's' or token[0] == 'a':
                                value = token[1]
                                value.replace(',', '.')
                                try:
                                    data[mapping[token[0]]] = float(value)
                                except:
                                    reponse = erreur_indic[token[0]]
                                    type_sms = 2
                            else:
                                try:
                                    data[mapping[token[0]]] = int(token[1])
                                except:
                                    reponse = erreur_indic[token[0]]
                                    type_sms = 2
                        else:
                            reponse = u"Diso! Tsy ao ny  kaody <.%s> sy ny valinteny mifanaraka aminy" % (token[0],)
                            type_sms = 2
                    else:
                        reponse = u"Tsy misy ny fanontaniana manana kaody <.%s>" % (token[0],)
                        type_sms = 2

                if type_sms == 1:
                    if data['femmes'] > data['certificats']:
                        reponse = u"Diso ! Ny isan'ny Karatany amin'ny anaran'ny vehivavy dia tokony ho latsaky ny isan'ny Karatany voasoratra"
                        type_sms = 2
                    else:
                        reponse = u"Misaotra tompoko! Voaray ny tatitra nalefanao."

    # limiter le nombre de caractere dans reponse a 158
    reponse = reponse[:158]
    return type_sms, reponse, data, texte


@login_required(login_url="/connexion")
def lister_communication(request):
    if request.method == 'GET':
        form = FiltreCommunicationForm()
    else:
        form = FiltreCommunicationForm(request.POST)
    page_js = '/media/js/sms/messages.js'
    title = 'Messages'
    return render_to_response('layout_list.html', {"form": form, "title": title, "page_js": page_js},
                              context_instance=RequestContext(request))


def ajax_communication(request):
    # columns titles
    columns = ['date_reception', 'commune', 'code', 'message']

    # filtering
    post = process_datatables_posted_vars(request.POST)
    kwargs = {}
    if 'fMessage' in post and post['fMessage'] != '':
        kwargs['message__icontains'] = post['fMessage']
    if 'fCreede' in post and post['fCreede'] != '':
        cree_de = datetime.strptime(post['fCreede'], "%d/%m/%Y")
        cree_de = datetime.strftime(cree_de, "%Y-%m-%d")
        kwargs['date_reception__gte'] = cree_de
    if 'fCreea' in post and post['fCreea'] != '':
        cree_a = datetime.strptime(post['fCreea'], "%d/%m/%Y")
        cree_a = datetime.strftime(cree_a, "%Y-%m-%d")
        kwargs['date_reception__lte'] = cree_a

    
    records, total_records, display_records = query_datatables(Communication, columns, post, **kwargs)
    results = []
    for row in records:
        checkbox = '<input type="checkbox" name=\"selected\" class="check-element" value="%s"/>' % row.id
        result = dict(
            date_reception = datetime.strftime(row.date_reception, "%d-%m-%Y %H:%M:%S"),
            commune = row.commune.nom,
            code = row.commune.code,
            message = row.message,
            checkbox = checkbox,
        )
        results.append(result)

    sEcho = int(post['sEcho'])
    results = {"iTotalRecords": total_records, "iTotalDisplayRecords":display_records, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')


def _inject_in_outbox(smsc, numero, texte):
    outgoing_sms = Outbox(
        updatedindb = datetime.now(),
        insertintodb = datetime.now(),
        sendingdatetime = datetime.now(),
        coding = 'Unicode_No_Compression',
        destinationnumber = numero,
        senderid = smsc,
        textdecoded = unicode(texte),
        multipart = False,
        sendingtimeout = datetime.now(),
        deliveryreport = 'no',
        creatorid = smsc,
        class_field = 0
    )
    outgoing_sms.save()


@login_required(login_url="/connexion")
def send_sms(smsc, numero, texte):
    _inject_in_outbox(smsc, numero, texte)

    envoi = Envoi(
        date_envoi = datetime.now(),
        destinataire = numero,
        message = texte
    )
    envoi.save()


def _get_operateur(numero):
    CODES = {'032': 'orange', '033': 'airtel', '034': 'telma'}
    if numero[:4] == '+261':
        code = '0%s' % (numero[4:2],)
    elif numero[:5] == '00261':
        code = '0%s' % (numero[5:2],)
    else:
        code = numero[:3]

    if code in CODES:
        operateur = CODES[code]
    else:
        operateur = None
    return operateur

def sms_broadcast(request):
    if request.method == 'GET':
        form = BroadcastForm()
        return render_to_response('sms/broadcast.html', {'form': form},
                                  context_instance=RequestContext(request))

    form = BroadcastForm(request.POST)
    texte = request.POST['message']
    numeros = request.POST['destinataire']
    numeros = numeros.split(',')

    for numero in numeros:
        operateur = _get_operateur(numero)
        if operateur is not None:
            send_sms(operateur, numero, texte)

    return HttpResponseRedirect(reverse(lister_envoi))


@login_required(login_url="/connexion")
def ajax_broadcast(request):
    # selectionner la liste des agf actifs de la localite ayant un num tel
    kwargs = {'etat': 1}
    if 'localite' in request.POST and request.POST['localite'] == 'region':
        kwargs['commune__district__region'] = int(request.POST['value'])
    if 'localite' in request.POST and request.POST['localite'] == 'district':
        kwargs['commune__district'] = int(request.POST['value'])
    if 'localite' in request.POST and request.POST['localite'] == 'commune':
        kwargs['commune'] = int(request.POST['value'])

    destinataires = Guichet.objects.filter(**kwargs).\
        exclude((Q(mobile1__isnull=True) | Q(mobile1__exact='')) & (Q(mobile2__isnull=True) | Q(mobile2__exact=''))).\
        values('mobile1', 'mobile2')

    numeros = []
    for row in destinataires:
        if row['mobile1'] is not None and row['mobile1'] != '':
            numeros.append(row['mobile1'])
        elif row['mobile2'] is not None and row['mobile2'] != '':
            numeros.append(row['mobile2'])

    results = {"numeros": numeros}
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')


@login_required(login_url="/connexion")
def export_communication(request, filetype=None):
    columns = [u'Date / Heure', u'Commune', u'Code', u'Message']
    dataset = Communication.objects.filter_for_xls(request.GET)
    if filetype == 'xls':
        response = export_excel(columns, dataset, 'messages')
    else:
        response = export_pdf(columns, dataset, 'messages')
    return response

@login_required(login_url="/connexion")
def supprimer_communication(request):
    if request.method == "POST":
        selected = request.POST.getlist("selected[]")
        obj = Communication.objects.filter(pk__in = selected)
    else:
        obj = get_object_or_404(Communication, pk=sms_id)
    obj.delete()
    json = simplejson.dumps([{'message': 'Enregistrement supprimé'}])
    return HttpResponse(json, mimetype='application/json')
# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from donnees.models import Donnees
from guichets.models import Guichet
from sms.models import Reception, Envoi
from sms.forms import FiltreEnvoiForm, FiltreReceptionForm, TesterForm
from helpers import paginate, export_excel, process_datatables_posted_vars
import re
from django.db.models import Q
import simplejson

def lister_reception(request):
    if request.method == 'GET':
        form = FiltreReceptionForm()
    else:
        form = FiltreReceptionForm(request.POST)
    return render_to_response('sms/lister_reception.html', {"form": form}, context_instance=RequestContext(request))

def ajax_reception(request):
    # columns titles
    columns = ['date_reception', 'numero', 'message', 'statut', 'reponse']

    # filtering
    posted = process_datatables_posted_vars(request.POST)

    kwargs = {}
    if 'fExpediteur' in posted and posted['fExpediteur'] != '':
        kwargs['expediteur__icontains'] = str(posted['fExpediteur'])
    if 'fMessage' in posted and posted['fMessage'] != '':
        kwargs['message__icontains'] = posted['fMessage']
    if 'fStatut' in posted and posted['fStatut'] != '':
        kwargs['statut'] = posted['fStatut']
    if 'fCreede' in posted and posted['fCreede'] != '':
        cree_de = datetime.strptime(posted['fCreede'], "%d/%m/%Y")
        cree_de = datetime.strftime(cree_de, "%Y-%m-%d")
        kwargs['date_reception__gte'] = cree_de
    if 'fCreea' in posted and posted['fCreea'] != '':
        cree_a = datetime.strptime(posted['fCreea'], "%d/%m/%Y")
        cree_a = datetime.strftime(cree_a, "%Y-%m-%d")
        kwargs['date_reception__lte'] = cree_a

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
    iTotalRecords = Reception.objects.count()
    if len(kwargs) > 0:
        if len(sorts) > 0:
            if lim_start is not None:
                reception = Reception.objects.filter(**kwargs).order_by(*sorts)[lim_start:lim_num]
            else:
                reception = Reception.objects.filter(**kwargs).order_by(*sorts)
        else:
            if lim_start is not None:
                reception = Reception.objects.filter(**kwargs)[lim_start:lim_num]
            else:
                reception = Reception.objects.filter(**kwargs)
        iTotalDisplayRecords = Reception.objects.filter(**kwargs).count()
    else:
        if len(sorts) > 0:
            if lim_start is not None:
                reception = Reception.objects.all().order_by(*sorts)[lim_start:lim_num]
            else:
                reception = Reception.objects.all().order_by(*sorts)
        else:
            if lim_start is not None:
                reception = Reception.objects.all()[lim_start:lim_num]
            else:
                reception = Reception.objects.all()
        iTotalDisplayRecords = iTotalRecords

    results = []

    for row in reception:
        result = dict(
            date_reception = datetime.strftime(row.date_reception, "%d-%m-%Y %H:%M:%S"),
            numero = row.expediteur,
            message = row.message,
            statut = row.get_statut_display(),
            reponse = row.retour,
        )
        results.append(result)

    sEcho = int(posted['sEcho'])
    results = {"iTotalRecords": iTotalRecords, "iTotalDisplayRecords":iTotalDisplayRecords, "sEcho": sEcho, "aaData": results}
    json = simplejson.dumps(results)

    return HttpResponse(json, mimetype='application/json')


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
                date_reception = datetime.now(),
                expediteur = request.POST['expediteur'],
                message = request.POST['message'],
                statut = 1,
                retour = message_retour
            )
            reception.save()

            donnees = Donnees(
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
        else:
            reception = Reception(
                date_reception = datetime.datetime.now(),
                expediteur = request.POST['expediteur'],
                message = request.POST['message'],
                statut = 2,
                retour = message_retour
            )
            reception.save()
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
    data = {}
    tokens = re.split(' \.', message)

    if len(tokens) < 12:
        return data, u"Erreur, Nombre de données insuffisant"

    if len(tokens) > 12:
        return data, u"Erreur, Nombre de données en dépassement"

    expediteur = tokens.pop(0)
    expediteur = expediteur.split('#')
    if len(expediteur) < 2:
        return data, u"Erreur, Code AGF ou mot de passe non fourni"
    elif len(expediteur) > 2:
        return data, u"Erreur, Code AGF erroné"
    else:
        # vérifier mot de passe
        # AGF048#0000 .p 11.2010 .d 1000 .o 1200 .r 2000 .c 3000 .f 0000 .t 1000 .a 1000000000 .s 0.233 .g 1000 .m 2000
        agf = Guichet.objects.filter((Q(agf1=expediteur[0]) & Q(password1=expediteur[1])) | (Q(agf2=expediteur[0]) & Q(password2=expediteur[1])))

        mapping = {'p': 'periode', 'd': 'demandes', 'o': 'oppositions', 'r': 'resolues', 'c': 'certificats', 'f': 'femmes',
                   't': 'reconnaissances', 'a': 'recettes', 's': 'surfaces', 'g': 'garanties', 'm': 'mutations'}
        # dict(p='periode', d='demandes', o='oppositions', r='resolues', c='certificats', f='femmes',
        #           t='reconnaissances', a='recettes', s='surfaces', g='garanties', m='mutations')

        if len(agf) == 1:
            agf = agf[0]
            data['commune'] = agf.commune
            for token in tokens:
                token = token.strip()
                token = token.split()
                if token[0] in mapping:
                    if token[0] == 'p':
                        periode = token[1].split('.')
                        if len(periode[0]) > 2 or len(periode[1]) < 4:
                            return data, u"Date erronée"
                        else:
                            data['periode'] = '%s-%s-01' % (periode[1], periode[0])
                    elif token[0] == 's' or token[0] == 'a':
                        value = token[1]
                        value.replace(',', '.')
                        data[mapping[token[0]]] = float(value)
                    else:
                        data[mapping[token[0]]] = token[1]
                else:
                    return data, u"Erreur, Code question '%s' inconnu" % token[0]
            # controle de coherence
            if data['femmes'] > data['certificats']:
                return data, u"Erreur, certificats donnés à des femmes ne peut dépasser le nombre de certificats délivrés"
            return data, u"Félicitations! Données enregistrées"
        else:
            return data, u"Code AGF ou mot de passe erroné"
# -*- coding: utf-8 -*-

import django
import datetime
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Count, Sum
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from localites.models import Region
from plots.forms import FiltreForm, FiltreRatioForm

import numpy as np
from donnees.models import Donnees, Cumul
from guichets.models import Guichet


XTICK = np.arange(12)
BARWIDTH = 0.4
MONTHS = ['Jan', u'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aou', 'Sep', 'Oct', 'Nov', u'Déc']

def graphe_guichets(request, year, region=None, output='page'):
    # nombre des nouveaux guichets par mois
    #guichets = get_monthly_aggregated_data('certificats', year, region)

    # nombre des certificats délivrés par mois
    certificats = get_monthly_aggregated_data('certificats', year, region)

    # nombre cumulé de certificats fonciers

    # nombre cumulé de guichets fonciers

    #region
    nom_region = ''
    if region is not None:
        obj = Region.objects.filter(pk=int(region))
        if len(obj) > 0:
            nom_region = obj[0].nom

    title = "Guichets fonciers - %s %s" % (nom_region, year)

    fig = Figure(facecolor='w')
    ax1 = fig.add_subplot(111, title=title)
    ax1.set_xticks(XTICK+BARWIDTH)
    ax1.set_xticklabels(MONTHS)

    # barres
    rect1 = []
    for i, key in enumerate(certificats):
        rect1.append(ax1.bar(i, certificats[key], BARWIDTH, color='y'))

    #rect2 = []
    #for i, key in enumerate(certificats):
    #    rect2.append(ax1.bar(i+BARWIDTH, certificats[key], BARWIDTH, color='g'))

    leg = ax1.legend((rect1[0]), ('Certificats',))
    _set_graph_fontstyle(ax1, leg)

    canvas = FigureCanvas(fig)
    if output == 'page':
        response = HttpResponse(content_type='image/png')
        canvas.print_png(response)

    return response


def graphe_demandes(request, year=None):
    ''' Donnees par region ou national sur une annee
    '''

    year = get_year(year)
    # nombre de demandes
    get_monthly_aggregated_data('demandes', year)

    # nombre de reconnaissances
    get_monthly_aggregated_data('reconnaissances', year)

    # nombre de certificats
    get_monthly_aggregated_data('certificats', year)

    pass


def graphe_ratio(request, year, ratio=0, region=None, output='page'):
    RATIOS = [{'key': 'rcertificats', 'label': u'Certification'},
            {'key': 'rfemmes', 'label': u'Certificats à des femmes'},
            {'key': 'rconflits', 'label': u'Conflictualité'},
            {'key': 'rresolus', 'label': u'Résolution'},
            {'key': 'rsurface', 'label': u'Surface moyen'}]

    ratios = get_monthly_aggregated_data(RATIOS[int(ratio)]['key'], year, region, cumul=True)

    nom_region = get_region(region)
    indicateur = RATIOS[int(ratio)]['label']

    title = "%s - %s %s" % (indicateur, nom_region, year)

    fig = Figure(facecolor='w')
    ax1 = fig.add_subplot(111, title=title)
    ax1.set_xticks(XTICK)
    ax1.set_xticklabels(MONTHS)

    # barres
    rect1 = ax1.plot(range(12), ratios, 'g-o')

    leg = ax1.legend((rect1[0],), (indicateur,))
    _set_graph_fontstyle(ax1, leg)

    canvas = FigureCanvas(fig)
    if output == 'page':
        response = HttpResponse(content_type='image/png')
        canvas.print_png(response)

    return response


def graphe_surface_moyen(request, year, region=None, output='page'):
    # surfaces en hectares
    surfaces = get_monthly_aggregated_data('surfaces', year, region)
    # nombre de certificats fonciers
    certificats = get_monthly_aggregated_data('certificats', year, region)

    nom_region = get_region(region)

    title = "Surfaces et certificats fonciers - %s %s" % (nom_region, year)

    fig = Figure(facecolor='w')
    ax1 = fig.add_subplot(111, title=title)
    ax1.set_xticks(XTICK+BARWIDTH)
    ax1.set_xticklabels(MONTHS)

    # barres
    rect1 = []
    for i, key in enumerate(surfaces):
        rect1.append(ax1.bar(i, surfaces[key], BARWIDTH, color='y'))

    rect2 = []
    for i, key in enumerate(certificats):
        rect2.append(ax1.bar(i+BARWIDTH, certificats[key], BARWIDTH, color='g'))

    leg = ax1.legend((rect1[0], rect2[0]), ('Surfaces', 'Certificats'))
    _set_graph_fontstyle(ax1, leg)

    canvas = FigureCanvas(fig)
    if output == 'page':
        response = HttpResponse(content_type='image/png')
        canvas.print_png(response)

    return response


def get_monthly_aggregated_data(indicateur, year, region=None, cumul=False):
    try:
        values = [0 for x in range(12)]
        if cumul:
            kwargs = {'periode__year': int(year)}
            if region != '0':
                kwargs['commune__district__region'] = int(region)
            obj = Cumul.objects.filter(**kwargs).values('periode').\
                        annotate(Count('periode'), sum=Sum(indicateur)).order_by('periode')
            for row in obj:
                if row['sum'] is not None:
                    values[row['periode'].month - 1] = row['sum']/row['periode__count']
                else:
                    values[row['periode'].month - 1] = 0
            data = values
        else:
            kwargs = {'valide': True, 'periode__year': int(year)}
            if region != '0':
                kwargs['commune__district__region'] = int(region)
            obj = Donnees.objects.filter(**kwargs).values('periode').\
                        annotate(Count('periode'), sum=Sum(indicateur)).order_by('periode')
            for row in obj:
                values[row['periode'].month - 1] = row['sum']
            data = {}
            i = 0
            for m in MONTHS:
                data[m] = values[i]
                i += 1
    except:
        data = None

    return data


def get_region(region_id):
    nom_region = ''
    if region_id is not None:
        obj = Region.objects.filter(pk=int(region_id))
        if len(obj) > 0:
            nom_region = obj[0].nom
    return nom_region


def get_year(year):
    if year is None:
        year = datetime.datetime.now().year
    return year


def _set_axe_fontstyle(ax):
    for t in ax.get_xticklabels():
        t.set_fontsize(10)
    for t in ax.get_yticklabels():
        t.set_fontsize(10)


def _set_graph_fontstyle(ax1, legend, ax2=None):
    _set_axe_fontstyle(ax1)
    if ax2 is not None:
        _set_axe_fontstyle(ax2)

    for t in legend.get_texts():
        t.set_fontsize(10)

def surface_moyen(request):
    year = datetime.datetime.now().year - 1
    form = FiltreForm(initial={'annee': year})
    region = 0
    if request.method == 'POST':
        form = FiltreForm(request.POST)
        year = request.POST['annee']
        if len(request.POST['region']) > 0:
            region = request.POST['region']

    year = get_year(year)
    graph = "surface_moyen_%s_%s.png" % (year, region)
    return render_to_response('plots/graph.html', {'form': form,
                                                   'graph': graph, 'title': 'Surface et certificat foncier'},
                                          context_instance=RequestContext(request))


def ratio(request):
    year = datetime.datetime.now().year - 1
    form = FiltreRatioForm(initial={'annee': year})
    region = ratio_id = 0
    if request.method == 'POST':
        form = FiltreRatioForm(request.POST)
        year = request.POST['annee']
        if len(request.POST['region']) > 0:
            region = request.POST['region']
        if len(request.POST['indicateur']) > 0:
            ratio_id = request.POST['indicateur']

    year = get_year(year)
    graph = "ratio_%s_%s_%s.png" % (year, ratio_id, region)
    return render_to_response('plots/graph.html', {'form': form,
                                                   'graph': graph, 'title': 'Ratios'},
                                          context_instance=RequestContext(request))


def guichet_foncier(request):
    year = datetime.datetime.now().year - 1
    form = FiltreForm(initial={'annee': year})
    region = 0
    if request.method == 'POST':
        form = FiltreForm(request.POST)
        year = request.POST['annee']
        if len(request.POST['region']) > 0:
            region = request.POST['region']

    year = get_year(year)
    graph = "guichet_foncier_%s_%s.png" % (year, region)
    return render_to_response('plots/graph.html', {'form': form,
                                                   'graph': graph, 'title': 'Guichets fonciers'},
                                          context_instance=RequestContext(request))


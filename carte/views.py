# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from django.db.models.aggregates import Count, Sum, Avg

from osgeo import ogr
import matplotlib.patches as rect
import matplotlib.font_manager as font
from descartes import PolygonPatch
import numpy as np
import datetime
from donnees.models import Cumul
from carte.forms import FiltreRatioForm, FiltreRMAForm, FiltreGuichetForm
from guichets.models import Rma, Guichet
from plots.views import get_year, get_region
from settings import PROJECT_DIR

MAP_LABELS = [u"de 0 à 0,25", u"de 0,25 à 0,5", u"de 0,5 à 0,75", u"de 0,75 à 1"]
RATIOS = [{'key': 'rcertificats', 'label': u'Taux de certification', 'colors': ['#d1ecfe', '#a6d8fd', '#6ca1fd', '#3377fc'], 'limits': [0.25, 0.5, 0.75], 'labels': MAP_LABELS},
            {'key': 'rfemmes', 'label': u'Taux de certificats à des femmes', 'colors': ['#f6d2ff', '#f1a7ff', '#e958fe', '#bc3a9a'], 'limits': [0.25, 0.5, 0.75], 'labels': MAP_LABELS},
            {'key': 'rconflits', 'label': u'Taux de conflictualité', 'colors': ['#fae9da', '#f9ca6d', '#f39a28', '#ef6e27'], 'limits': [0.25, 0.5, 0.75], 'labels': MAP_LABELS},
            {'key': 'rresolus', 'label': u'Taux de résolution', 'colors': ['#ec3626', '#f39a41', '#7ccdfd', '#3d9bca'], 'limits': [0.25, 0.5, 0.75], 'labels': MAP_LABELS},
            {'key': 'rsurface', 'label': u'Surface moyen', 'colors': ['#d6facc', '#b2f89a', '#93f568', '#67c336', '#387a06'], 'limits': [0.25, 0.75, 2.5, 5],
             'labels': [u"de 0 à 0,25", u"de 0,25 à 0,75", u"de 0,75 à 2,5", u"de 2,5 à 5", u"plus de 5"]},
            {'key': 'rma', 'label': u"Etat d'envoi des RMA", 'colors': ['#4fa950', '#E8ED6F', '#E01714'], 'limits': [1, 2, 3], 'labels': [u"avant le 10", u"après le 10", u"non envoyé"]},
            {'key': 'guichet', 'label': u"Guichets fonciers", 'colors': ['#4fa950', '#E01714', '#E8ED6F'], 'limits': [1, 3, 4], 'labels': [u"Ouvert", u"Suspendu ou fermé", u"En constitution"]}
    ]

def _create_legende(axe, labels, colors):
    legsize = font.FontProperties(size=11)
    p = [rect.Rectangle((0,0), 1, 1, fc=color, ec='#555555') for color in colors]
    axe.legend(p, labels, loc=4, prop=legsize, frameon=False)


def _get_carte_carte(region, communes, ratio=None, title=""):
    # Create a figure plot
    fig = Figure(facecolor='w', figsize=(13, 13), dpi=72)
    ax = fig.add_subplot(111, aspect='equal', frameon=False, title=title)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # Open a shapefile
    shpFile = ogr.Open(PROJECT_DIR + "/media/shapefiles/commune.shp")
    layer = shpFile.GetLayer(0)

    # Liste des communes
    feature = layer.GetNextFeature()

    while feature is not None:
        if feature.GetField('REGION') == region.upper():
            geom = feature.GetGeometryRef()

            nom_commun = feature.GetField('NOM_COMMUN').upper()
            if nom_commun in communes:
                fcolor = communes[nom_commun]
            else:
                fcolor = '#FFFFFF'

            if geom.GetGeometryCount() < 2:
                geomPnt = geom.GetGeometryRef(0)
                points=[]
                for i in range(0,geomPnt.GetPointCount()):
                    geomPntX = geomPnt.GetX(i)
                    geomPntY = geomPnt.GetY(i)
                    points.append([geomPntX,geomPntY])
                # This is a geoJSON-­‐like object
                polygon = {"type": "Polygon","coordinates":[points]}
                patch =	PolygonPatch(polygon, fc=fcolor, ec='#999999')
                ax.add_patch(patch)

            for geomcnt in range(0,geom.GetGeometryCount()):
                multifeat =	 geom.GetGeometryRef(geomcnt)
                # This is the loop that deals with multifeature	records.
                for i in range(0, multifeat.GetGeometryCount()):
                    geomPnt = multifeat.GetGeometryRef(i)
                    points =[]
                    for j in range(0,geomPnt.GetPointCount()):
                        geomPntX = geomPnt.GetX(i)
                        geomPntY = geomPnt.GetY(i)
                        points.append([geomPntX,geomPntY])
                    # Unfortunately descartes doesn't support 'MultiPolygon'
                    # luckily it's not an issue with this shapefile
                    polygon = {"type": "Polygon","coordinates":[points]}
                    patch = PolygonPatch(polygon, fc=fcolor, ec='#999999')
                    ax.add_patch(patch)

        feature = layer.GetNextFeature()

    # Resize de la carte
    ax.autoscale()
    # legende
    colors = RATIOS[int(ratio)]['colors']
    labels = RATIOS[int(ratio)]['labels']
    _create_legende(ax, labels, colors)

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response


def _get_color_for_commune(ratio, value):
    colors = RATIOS[int(ratio)]['colors']
    limits = RATIOS[int(ratio)]['limits']

    for i in range(len(limits)):
        if value <= limits[i]:
            return colors[i]

    return colors[i]


def carte_ratio(request, year=None, ratio=0, region=None, output='page'):
    # param
    year = get_year(year)
    nom_region = get_region(region).upper()
    indicateur = RATIOS[int(ratio)]['label']

    # retrouver les donnees
    ratios = Cumul.objects.filter(periode__year=year, commune__district__region=int(region)).\
            values('commune__nom').annotate(Count('commune'), avg=Avg('rcertificats'))

    # formatage des donnees
    communes = {}
    for item in ratios:
        communes[item['commune__nom']] = _get_color_for_commune(ratio, item['avg'])


    # titre de la carte
    title = "%s - %s %s" % (indicateur, nom_region, year)

    # reponse
    response = _get_carte_carte(nom_region, communes, ratio, title)

    return response


@login_required(login_url="/connexion")
def ratio(request, ratio=0):
    year = datetime.datetime.now().year - 1
    form = FiltreRatioForm(initial={'annee': year, 'region': 1})
    region = 1
    if request.method == 'POST':
        form = FiltreRatioForm(request.POST)
        year = request.POST['annee']
        if len(request.POST['region']) > 0:
            region = request.POST['region']

    year = get_year(year)
    carte = "carte_%s_%s_%s.png" % (year, ratio, region)
    return render_to_response('carte/carte.html', {'form': form,
                                                   'carte': carte, 'title': 'Ratios'},
                                          context_instance=RequestContext(request))


def carte_rma(request, periode=None, region=None, output='page'):
    # param
    periode_reference = "01/%s/%s" % (periode[2:4], periode[4:8])
    mois = "%s-%s" % (periode[2:4], periode[4:8])
    periode = "%s-%s-01" % (periode[4:8], periode[2:4])
    reference = datetime.datetime.strptime(periode_reference, "%d/%m/%Y")

    nom_region = get_region(region).upper()

    # retrouver les donnees
    rapports = Rma.objects.filter(periode=periode, guichet__commune__district__region=int(region))\
                    .values('guichet__commune__nom', 'sms')

    # formatage des donnees
    communes = {}
    for item in rapports:
        if item['sms'] is not None:
            reception = item['sms'].date_reception
            retard = reception - reference
            retard = 2
        else:
            retard = 3
        communes[item['guichet__commune__nom']] = _get_color_for_commune(5, retard)


    # titre de la carte
    title = "Envoi des RMA - %s %s" % (nom_region, mois)

    # reponse
    response = _get_carte_carte(nom_region, communes, 5, title)

    return response


@login_required(login_url="/connexion")
def etat_rma(request):
    today = datetime.date.today() - datetime.timedelta(days=31)
    periode_url_formatted = "01%02d%s" % (today.month, today.year)
    form = FiltreRMAForm(initial={'periode': "%02d/%s" % (today.month, today.year), 'region': 1})
    region = 1
    if request.method == 'POST':
        form = FiltreRMAForm(request.POST)
        periode = request.POST['periode']
        periode_url_formatted = "01%s%s" % (periode[:2], periode[3:7])
        if len(request.POST['region']) > 0:
            region = request.POST['region']


    carte = "rma_%s_%s.png" % (periode_url_formatted, region)
    return render_to_response('carte/carte.html', {'form': form,
                                                   'carte': carte, 'title': "Etat d'envoi des RMA"},
                                          context_instance=RequestContext(request))


def carte_guichet(request, region=None, output='page'):
    # param
    nom_region = get_region(region).upper()

    # retrouver les donnees
    guichets = Guichet.objects.filter(commune__district__region=int(region))\
                    .values('commune__nom', 'etat')

    # formatage des donnees
    communes = {}
    for item in guichets:
        communes[item['commune__nom']] = _get_color_for_commune(6, int(item['etat']))


    # titre de la carte
    title = "Guichets fonciers - %s" % (nom_region,)

    # reponse
    response = _get_carte_carte(nom_region, communes, 6, title)

    return response

@login_required(login_url="/connexion")
def guichet(request):
    form = FiltreGuichetForm(initial={'region': 1})
    region = 1
    if request.method == 'POST':
        form = FiltreGuichetForm(request.POST)
        if len(request.POST['region']) > 0:
            region = request.POST['region']


    carte = "guichet_%s.png" % (region)
    return render_to_response('carte/carte.html', {'form': form,
                                                   'carte': carte, 'title': "Guichets fonciers"},
                                          context_instance=RequestContext(request))

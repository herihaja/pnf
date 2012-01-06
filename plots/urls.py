# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from plots.views import graphe_surface_moyen, surface_moyen, graphe_guichets, guichet_foncier, ratio, graphe_ratio

urlpatterns = patterns('',
                        (r'surface_moyen_(?P<year>.+?)_(?P<region>.+?).png', graphe_surface_moyen),
                        (r'guichet_foncier_(?P<year>.+?)_(?P<region>.+?).png', graphe_guichets),
                        (r'ratio_(?P<year>.+?)_(?P<region>.+?).png', graphe_ratio),
                        (r'^graphe/surfaces-moyens/$', surface_moyen),
                        (r'^graphe/guichets-fonciers/$', guichet_foncier),
                        (r'^graphe/ratios/$', ratio),
                    )

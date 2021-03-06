# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from donnees.views import lister_cumuls
from indicateurs.views import indicateurs_par_date, indicateur_par_date, ratio, ajax_pivot_table, ajax_indicateurs, export_indicateurs, export_ratios

urlpatterns = patterns('',
                        (r'^indicateurs/tout/$', indicateurs_par_date),
                        (r'^indicateurs/export/(?P<filetype>.+?)/', export_indicateurs),
                        (r'^indicateurs/un/$', indicateur_par_date),
                        (r'^indicateurs/cumuls/$', lister_cumuls),
                        (r'^ratios/certification/$', ratio, {'ratio': 'rcertificats', 'title': 'Taux de certification'}),
                        (r'^ratios/certification-aux-femmes/$', ratio, {'ratio': 'rfemmes', 'title': 'Taux de certificats accordés aux femmes'}),
                        (r'^ratios/conflictualite/$', ratio, {'ratio': 'rconflits', 'title': 'Taux de conflictualité'}),
                        (r'^ratios/resolution/$', ratio, {'ratio': 'rresolus', 'title': 'Taux de résolution'}),
                        (r'^ratios/surface-moyen/$', ratio, {'ratio': 'rsurface', 'title': 'Surface moyen'}),
                        (r'^indicateurs/annees/ajax/$', ajax_pivot_table),
                        (r'^indicateurs/ajax/$', ajax_indicateurs),
                        (r'^ratios/export/(?P<filetype>.+?)/', export_ratios),
                    )

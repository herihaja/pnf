# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from carte.views import carte_ratio, ratio, etat_rma, carte_rma, carte_guichet, guichet

urlpatterns = patterns('',
                        (r'carte_(?P<year>.+?)_(?P<ratio>.+?)_(?P<region>.+?).png', carte_ratio),
                        (r'rma_(?P<periode>.+?)_(?P<region>.+?).png', carte_rma),
                        (r'guichet_(?P<region>.+?).png', carte_guichet),
                        (r'^carte/taux-de-certification/$', ratio, {'ratio': 0}),
                        (r'^carte/certificats-femmes/$', ratio, {'ratio': 1}),
                        (r'^carte/taux-de-conflictualite/$', ratio, {'ratio': 2}),
                        (r'^carte/taux-de-resolution/$', ratio, {'ratio': 3}),
                        (r'^carte/surface-moyen/$', ratio, {'ratio': 4}),
                        (r'^carte/rma/$', etat_rma),
                        (r'^carte/guichets/$', guichet),
                    )

# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from donnees.views import lister_cumuls
from indicateurs.views import indicateurs_par_date, indicateur_par_date, ratio

urlpatterns = patterns('',
                        (r'^indicateurs/tout/$', indicateurs_par_date),
                        (r'^indicateurs/un/$', indicateur_par_date),
                        (r'^indicateurs/cumuls/$', lister_cumuls),
                        (r'^ratios/certification/$', ratio, {'numerateur':'certificats', 'denominateur':'demandes', 'titre': 'Taux de certification'}),
                        (r'^ratios/certification-aux-femmes/$', ratio, {'numerateur':'femmes', 'denominateur':'certificats', 'titre': 'Taux de certificats accordés aux femmes'}),
                        (r'^ratios/conflictualite/$', ratio, {'numerateur':'oppositions', 'denominateur':'demandes', 'titre': 'Taux de conflictualité'}),
                        (r'^ratios/resolution/$', ratio, {'numerateur':'resolues', 'denominateur':'oppositions', 'titre': 'Taux de résolution'}),
                        (r'^ratios/surface-moyen/$', ratio, {'numerateur':'surfaces', 'denominateur':'certificats', 'titre': 'Surface moyen'}),
                    )

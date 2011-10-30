# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from indicateurs.views import indicateurs_par_date, indicateur_par_date, ratio

urlpatterns = patterns('',
                        (r'^indicateurs/tout/$', indicateurs_par_date),
                        (r'^indicateurs/un/$', indicateur_par_date),
                        (r'^ratios/certification/$', ratio, {'numerateur':'certificats', 'denominateur':'demandes'}),
                        (r'^ratios/certification-aux-femmes/$', ratio, {'numerateur':'femmes', 'denominateur':'certificats'}),
                        (r'^ratios/conflictualite/$', ratio, {'numerateur':'oppositions', 'denominateur':'demandes'}),
                        (r'^ratios/resolution/$', ratio, {'numerateur':'resolues', 'denominateur':'oppositions'}),
                        (r'^ratios/surface-moyen/$', ratio, {'numerateur':'surfaces', 'denominateur':'certificats'}),
                    )

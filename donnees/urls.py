# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from donnees.views import ajouter_donnees, editer_donnees, lister_recu, supprimer_recu, \
    supprimer_donnees, lister_cumuls, ajax_donnees, ajax_cumuls, export_cumuls, export_donnees, ajax_recu, tester_recu, valider_recu, lister_donnees, exporter_pour_site, export_site, export_recu, lister_rejete, ajax_rejete, rejeter_recu, export_rejete

urlpatterns = patterns('',
                        (r'donnees/$', lister_donnees),
                        (r'^donnees/recues/$', lister_recu),
                        (r'^donnees/rejetees/$', lister_rejete),
                        (r'^donnees/ajout/$', ajouter_donnees),
                        (r'^recu/ajax/$', ajax_recu),
                        (r'^rejete/ajax/$', ajax_rejete),
                        (r'^recu/export/(?P<filetype>.+?)/$', export_recu),
                        (r'^recu/supprimer/(?P<recu_id>.+?)$', supprimer_recu),
                        (r'^recu/valider/(?P<recu_id>.+?)$', valider_recu),
                        (r'^recu/rejeter/(?P<recu_id>.+?)$', rejeter_recu),
                        (r'^rejete/export/(?P<filetype>.+?)/$', export_rejete),
                        (r'^donnees/tester/(?P<recu_id>.+?)$', tester_recu),
                        (r'^donnees/ajax/$', ajax_donnees),
                        (r'^donnees/export/(?P<filetype>.+?)/$', export_donnees),
                        (r'^donnees/editer/(?P<donnee_id>.+?)$', editer_donnees),
                        (r'^donnees/supprimer/(?P<donnee_id>.+?)$', supprimer_donnees),
                        (r'^cumuls/$', lister_cumuls),
                        (r'^cumuls/ajax/$', ajax_cumuls),
                        (r'^cumuls/export/(?P<filetype>.+?)/$', export_cumuls),
                        (r'^export-site/$', exporter_pour_site),
                        (r'^export-site/export/$', export_site)
                    )

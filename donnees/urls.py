# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from donnees.views import ajouter_donnees, editer_donnees, lister_recu, supprimer_recu, \
    supprimer_donnees, lister_cumuls, ajax_donnees, ajax_cumuls, export_cumuls, export_donnees, ajax_recu, tester_recu, valider_recu

urlpatterns = patterns('',
                        (r'^donnees/recues/$', lister_recu),
                        (r'^donnees/ajout/$', ajouter_donnees),
                        (r'^recu/ajax/$', ajax_recu),
                        (r'^donnees/tester/(?P<recu_id>.+?)$', tester_recu),
                        (r'^donnees/ajax/$', ajax_donnees),
                        (r'^donnees/export/$', export_donnees),
                        (r'^donnees/editer/(?P<donnee_id>.+?)$', editer_donnees),
                        (r'^donnees/supprimer/(?P<donnee_id>.+?)$', supprimer_donnees),
                        (r'^recu/supprimer/(?P<recu_id>.+?)$', supprimer_recu),
                        (r'^recu/valider/(?P<recu_id>.+?)$', valider_recu),
                        (r'^cumuls/$', lister_cumuls),
                        (r'^cumuls/ajax/$', ajax_cumuls),
                        (r'^cumuls/export/$', export_cumuls),
                    )
